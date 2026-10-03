"""Provider execution boundary shared by deterministic and real adapters."""
from dataclasses import dataclass, field
from typing import Callable


class ProviderError(RuntimeError):
    """Base provider error with explicit dispatch certainty."""

    def __init__(self, message: str, *, retryable: bool = False, dispatched: bool = False,
                 retry_after: int | None = None, safe_to_resubmit: bool = False):
        super().__init__(message)
        self.retryable = retryable
        self.dispatched = dispatched
        self.retry_after = retry_after
        self.safe_to_resubmit = safe_to_resubmit


class ProviderUnavailable(ProviderError):
    pass


class ProviderRateLimited(ProviderError):
    """The provider explicitly rejected this call and supplied retry guidance."""

    def __init__(self, message: str, *, retry_after: int | None = None,
                 dispatched: bool = False, safe_to_resubmit: bool = False):
        super().__init__(message, retryable=True, dispatched=dispatched,
            retry_after=retry_after, safe_to_resubmit=safe_to_resubmit)


class ProviderPollingRetryable(ProviderError):
    """A read-only status operation may safely be retried."""

    def __init__(self, message: str, *, retry_after: int | None = None):
        super().__init__(message, retryable=True, dispatched=False, retry_after=retry_after)


@dataclass(frozen=True)
class ProviderOutcome:
    status: str
    provider_job_id: str = ""
    result_url: str = ""
    file_reference: str = ""
    response: dict = field(default_factory=dict)
    usage: dict = field(default_factory=dict)
    cost: str | None = None
    currency: str = ""
    error: str = ""


@dataclass(frozen=True)
class ProviderCapabilities:
    provider: str
    models: tuple[str, ...]
    text_to_video: bool
    image_to_video: bool
    reference_image: bool
    negative_prompt: bool
    cancellation: bool
    reconciliation: bool
    webhook: bool
    duration_min: int
    duration_max: int
    text_ratios: tuple[str, ...]
    image_ratios: tuple[str, ...]
    supported_resolutions: tuple[str, ...]


class VideoProviderAdapter:
    capabilities: ProviderCapabilities

    def submit(self, request, *, on_dispatch: Callable[[], None], technical_attempt: int = 1) -> ProviderOutcome:
        raise NotImplementedError

    def poll(self, request, *, poll_sequence: int) -> ProviderOutcome:
        raise NotImplementedError

    def cancel(self, request) -> ProviderOutcome:
        raise NotImplementedError

    def reconcile(self, request) -> ProviderOutcome:
        raise NotImplementedError

    def test_connection(self) -> dict:
        raise NotImplementedError

    def poll_interval_seconds(self, request) -> int:
        return max(0, int((request.generation_config or {}).get("poll_interval_seconds", 5)))


class FakeVideoProvider(VideoProviderAdapter):
    """No network or mutable memory; behavior derives entirely from saved request config."""

    capabilities = ProviderCapabilities(
        provider="Fake", models=("fake-v1",), text_to_video=True,
        image_to_video=True, reference_image=True, negative_prompt=True,
        cancellation=True, reconciliation=True, webhook=False, duration_min=1, duration_max=3600,
        text_ratios=("1280:720", "720:1280", "960:960"),
        image_ratios=("1280:720", "720:1280", "960:960"),
        supported_resolutions=("720p",),
    )

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

    def test_connection(self):
        return {"ok": True, "message": "Fake provider ready"}


def get_video_provider(provider: str) -> VideoProviderAdapter:
    if provider.lower() in {"fake", "mock"}:
        return FakeVideoProvider()
    if provider.lower() == "runway":
        from .runway_provider import RunwayVideoProvider
        return RunwayVideoProvider()
    raise ProviderUnavailable(f"Provider adapter is not configured: {provider}", retryable=False, dispatched=False)
