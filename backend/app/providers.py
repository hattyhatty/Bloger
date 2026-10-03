"""Provider execution boundary. Phase 8B.5B ships only deterministic FakeVideoProvider."""
from dataclasses import dataclass, field
from typing import Callable


class ProviderError(RuntimeError):
    """Base provider error with explicit dispatch certainty."""

    def __init__(self, message: str, *, retryable: bool = False, dispatched: bool = False):
        super().__init__(message)
        self.retryable = retryable
        self.dispatched = dispatched


class ProviderUnavailable(ProviderError):
    pass


@dataclass(frozen=True)
class ProviderOutcome:
    status: str
    provider_job_id: str = ""
    result_url: str = ""
    file_reference: str = ""
    response: dict = field(default_factory=dict)
    usage: dict = field(default_factory=dict)
    error: str = ""


class VideoProviderAdapter:
    def submit(self, request, *, on_dispatch: Callable[[], None], technical_attempt: int = 1) -> ProviderOutcome:
        raise NotImplementedError

    def poll(self, request, *, poll_sequence: int) -> ProviderOutcome:
        raise NotImplementedError

    def cancel(self, request) -> ProviderOutcome:
        raise NotImplementedError

    def reconcile(self, request) -> ProviderOutcome:
        raise NotImplementedError


class FakeVideoProvider(VideoProviderAdapter):
    """No network or mutable memory; behavior derives entirely from saved request config."""

    def _mode(self, request):
        return (request.generation_config or {}).get("fake_mode", "immediate_success")

    def _job_id(self, request):
        return "fake-job-" + request.logical_key[:20]

    def _result(self, request):
        return "https://fake.invalid/video/" + request.logical_key[:24] + ".mp4"

    def submit(self, request, *, on_dispatch, technical_attempt=1):
        mode = self._mode(request)
        transient_count = int((request.generation_config or {}).get("transient_failures", 1))
        if mode == "retryable_error" and technical_attempt <= transient_count:
            raise ProviderUnavailable("Fake temporary failure before dispatch", retryable=True, dispatched=False)
        on_dispatch()
        if mode == "transport_unknown":
            raise ProviderUnavailable("Fake timeout after dispatch", retryable=False, dispatched=True)
        if mode == "definitive_failure":
            return ProviderOutcome("failed", error="Fake provider rejected the request")
        if mode in {"async_success", "async_failure", "not_ready", "reconcile_success", "reconcile_failure"}:
            return ProviderOutcome("submitted", provider_job_id=self._job_id(request), response={"accepted": True})
        return ProviderOutcome("succeeded", provider_job_id=self._job_id(request), result_url=self._result(request),
            response={"status": "completed", "resultUrl": self._result(request)}, usage={"fakeUnits": 1})

    def poll(self, request, *, poll_sequence):
        mode = self._mode(request)
        if mode == "async_failure":
            return ProviderOutcome("failed", provider_job_id=request.provider_job_id, error="Fake asynchronous failure")
        ready_after = int((request.generation_config or {}).get("ready_after_polls", 2))
        if mode == "not_ready" or poll_sequence < ready_after:
            return ProviderOutcome("pending", provider_job_id=request.provider_job_id, response={"status": "processing"})
        return ProviderOutcome("succeeded", provider_job_id=request.provider_job_id, result_url=self._result(request),
            response={"status": "completed", "resultUrl": self._result(request)}, usage={"fakeUnits": 2})

    def cancel(self, request):
        if not (request.generation_config or {}).get("cancel_supported", True):
            return ProviderOutcome("unsupported", provider_job_id=request.provider_job_id,
                error="Fake provider does not support cancellation")
        return ProviderOutcome("cancelled", provider_job_id=request.provider_job_id, response={"cancelled": True})

    def reconcile(self, request):
        mode = (request.generation_config or {}).get("reconcile_outcome") or self._mode(request)
        if mode == "reconcile_success":
            return ProviderOutcome("succeeded", provider_job_id=request.provider_job_id or self._job_id(request),
                result_url=self._result(request), response={"reconciled": True, "resultUrl": self._result(request)})
        if mode == "reconcile_failure":
            return ProviderOutcome("failed", provider_job_id=request.provider_job_id or self._job_id(request),
                error="Fake reconciliation confirmed failure")
        return ProviderOutcome("unknown", provider_job_id=request.provider_job_id, error="Fake provider has no definitive state")


def get_video_provider(provider: str) -> VideoProviderAdapter:
    if provider.lower() in {"fake", "mock"}:
        return FakeVideoProvider()
    raise ProviderUnavailable(f"Provider adapter is not configured: {provider}", retryable=False, dispatched=False)
