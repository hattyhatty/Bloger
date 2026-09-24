import json
import re

from .models import KnowledgeEntry


def safe_filename(value: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|#\[\]]+', "-", value or "untitled").strip(" .-")
    return f"{cleaned or 'untitled'}.md"


def knowledge_to_markdown(item: KnowledgeEntry) -> str:
    tags = [str(tag).replace(" ", "-") for tag in (item.tags or []) if str(tag).strip()]
    source_link = item.source_url or item.raw.get("sourceUrl") or item.raw.get("source") or ""
    linked_topic = item.topic_id or item.raw.get("linkedTopicId") or item.raw.get("primaryTopicId") or ""
    linked_content_ids = item.raw.get("linkedContentIds") if isinstance(item.raw.get("linkedContentIds"), list) else []
    linked_content = item.content_id or (linked_content_ids[0] if linked_content_ids else "")
    frontmatter = [
        "---",
        f"title: {json.dumps(item.title, ensure_ascii=False)}",
        f"knowledge_type: {json.dumps(item.knowledge_type, ensure_ascii=False)}",
        f"source: {json.dumps(item.source, ensure_ascii=False)}",
        f"source_url: {json.dumps(source_link or '', ensure_ascii=False)}",
        f"confidence: {item.confidence}",
        f"status: {json.dumps(item.status, ensure_ascii=False)}",
        f"topic_id: {json.dumps(linked_topic, ensure_ascii=False)}",
        f"content_id: {json.dumps(linked_content, ensure_ascii=False)}",
        f"tags: {json.dumps(tags, ensure_ascii=False)}",
        f"created_at: \"{item.created_at.isoformat() if item.created_at else ''}\"",
        f"updated_at: \"{item.updated_at.isoformat() if item.updated_at else ''}\"",
        "---",
        ""
    ]
    trust_note = ["> ⚠️ This entry is an inference, not a verified fact.", ""] if item.knowledge_type == "Inference" else [""]
    body = [
        f"# {item.title}",
        "",
        f"> Type: {item.knowledge_type} · Confidence: {item.confidence}/100 · Status: {item.status}",
        *trust_note,
        item.body or item.raw.get("summary") or item.raw.get("eventSummary") or "",
        "",
        "## Source",
        f"- Name: {item.source or 'N/A'}",
        f"- URL: {source_link or 'N/A'}",
        "",
        "## Links",
        f"- Topic: {linked_topic or 'N/A'}",
        f"- Content: {linked_content or 'N/A'}",
        "",
        "## Tags",
        " ".join(f"#{tag}" for tag in tags) if tags else "N/A",
        ""
    ]
    return "\n".join(frontmatter + body)
