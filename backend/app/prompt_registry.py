"""Code-owned templates; template version is NOT an artifact revision."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .workflow import WorkflowConflict


@dataclass(frozen=True)
class PromptTemplate:
    prompt_key: str
    content: str
    version: str
    hash: str


def template_from_content(key: str, content: str) -> PromptTemplate:
    digest = sha256(content.encode("utf-8")).hexdigest()
    return PromptTemplate(key, content, digest, digest)


class PromptRegistry:
    templates = {"video.generate": "video_generation.txt", "research.analyze": "research_analysis.txt"}

    @classmethod
    def get(cls, key: str) -> PromptTemplate:
        filename = cls.templates.get(key)
        if not filename:
            raise WorkflowConflict("Unknown prompt template")
        content = (Path(__file__).resolve().parents[1] / "prompts" / filename).read_text(encoding="utf-8").replace("\r\n", "\n")
        return template_from_content(key, content)
