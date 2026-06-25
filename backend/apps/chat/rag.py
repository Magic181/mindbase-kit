import os
import re
import time
from dataclasses import dataclass
from typing import Any

import requests
from requests import exceptions as request_exceptions
from django.db.models import Q

from apps.documents.models import DocumentChunk, DocumentStatus

from .web_search import WebResult


@dataclass(frozen=True)
class Citation:
    document_id: int
    document_name: str
    chunk_id: int
    chunk_text: str
    position: int


class DeepSeekError(RuntimeError):
    user_message = "AI 服务暂时不可用，请稍后重试。"


class DeepSeekConfigError(DeepSeekError):
    user_message = "AI 服务配置不完整，请检查 DeepSeek API Key。"


class DeepSeekAuthError(DeepSeekError):
    user_message = "AI 服务认证失败，请检查 DeepSeek API Key。"


class DeepSeekRequestError(DeepSeekError):
    user_message = "AI 请求参数无效，请检查模型配置。"


def _tokenize(query: str) -> list[str]:
    query = query.strip().lower()
    if not query:
        return []
    tokens = re.split(r'[\s,，.。;；:：!?！？()\[\]{}"“”\'`]+', query)
    return [t for t in tokens if len(t) >= 2][:8]


def retrieve_citations(notebook_id: int, query: str, top_k: int = 5) -> list[Citation]:
    tokens = _tokenize(query)
    qs = DocumentChunk.objects.select_related('document').filter(
        document__notebook_id=notebook_id,
        document__status=DocumentStatus.COMPLETED,
    )

    if tokens:
        token_q = Q()
        for t in tokens:
            token_q |= Q(content__icontains=t)
        qs = qs.filter(token_q)

    chunks = list(qs.order_by('-id')[: max(top_k * 3, top_k)])

    def score(chunk: DocumentChunk) -> int:
        text = (chunk.content or '').lower()
        return sum(text.count(t) for t in tokens) if tokens else 0

    chunks.sort(key=score, reverse=True)
    chunks = chunks[:top_k]

    citations: list[Citation] = []
    for c in chunks:
        doc = c.document
        citations.append(
            Citation(
                document_id=doc.id,
                document_name=doc.name,
                chunk_id=c.id,
                chunk_text=c.content[:500],
                position=c.position,
            )
        )
    return citations


def build_prompt(
    query: str,
    citations: list[Citation],
    max_context_chars: int = 8000,
    web_results: list[WebResult] | None = None,
) -> list[dict[str, Any]]:
    context_blocks: list[str] = []
    remaining = max_context_chars
    for idx, c in enumerate(citations, start=1):
        block = f"[{idx}] 文档：{c.document_name}（chunk#{c.position}）\n{c.chunk_text}".strip()
        if len(block) > remaining:
            block = block[:remaining]
        if not block:
            break
        context_blocks.append(block)
        remaining -= len(block) + 2
        if remaining <= 0:
            break

    web_results = web_results or []
    for idx, result in enumerate(web_results, start=1):
        block = (
            f"[W{idx}] 网页：{result.title}\n"
            f"链接：{result.url}\n"
            f"{result.content}"
        ).strip()
        if len(block) > remaining:
            block = block[:remaining]
        if not block:
            break
        context_blocks.append(block)
        remaining -= len(block) + 2
        if remaining <= 0:
            break

    system = (
        "你是 AI Notebook 的助手，可以帮助用户理解资料、整理知识和进行基础问答。\n"
        "回答规则：\n"
        "- 对问候、助手能力、模型身份、产品使用方式等通用问题，可以直接自然回答。\n"
        "- 对要求总结、解释、查找或引用 Notebook 资料的问题，必须优先基于资料片段回答。\n"
        "- 若提供了网页搜索结果，可以结合网页内容回答，并引用网页编号，如 [W1][W2]。\n"
        "- 如果资料型问题缺少足够资料，说明“资料不足”，并给出还需要的资料类型。\n"
        "- 使用资料片段时，尽量引用片段编号，如 [1][2]。\n"
        "- 回答要简洁、结构清晰。\n"
    )

    context = "\n\n".join(context_blocks) if context_blocks else ""
    user = f"用户问题：{query}\n\n资料片段：\n{context}" if context else f"用户问题：{query}\n\n资料片段：无"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def call_deepseek_chat(messages: list[dict[str, Any]]) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise DeepSeekConfigError("DEEPSEEK_API_KEY 未配置")

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    retries = int(os.getenv("DEEPSEEK_MAX_RETRIES", "2"))
    backoff = float(os.getenv("DEEPSEEK_RETRY_BACKOFF_SECONDS", "0.2"))
    timeout = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60"))

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = _post_with_retries(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _post_with_retries(
    url: str,
    headers: dict[str, str],
    json: dict[str, Any],
    timeout: float,
    retries: int,
    backoff: float,
) -> requests.Response:
    last_error: Exception | None = None
    attempts = max(1, retries + 1)

    for attempt in range(attempts):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )
            _raise_for_deepseek_status(response)
            return response
        except (DeepSeekAuthError, DeepSeekRequestError):
            raise
        except (
            request_exceptions.Timeout,
            request_exceptions.ConnectionError,
            request_exceptions.ChunkedEncodingError,
            DeepSeekError,
        ) as exc:
            last_error = exc
            if attempt >= attempts - 1:
                break
            if backoff > 0:
                time.sleep(backoff * (attempt + 1))

    raise DeepSeekError(str(last_error or "DeepSeek request failed"))


def _raise_for_deepseek_status(response: requests.Response) -> None:
    status_code = response.status_code
    if status_code < 400:
        return
    if status_code in (401, 403):
        raise DeepSeekAuthError(_safe_error_text(response))
    if status_code in (400, 404):
        raise DeepSeekRequestError(_safe_error_text(response))
    if status_code == 429 or status_code >= 500:
        raise DeepSeekError(_safe_error_text(response))
    raise DeepSeekRequestError(_safe_error_text(response))


def _safe_error_text(response: requests.Response) -> str:
    return response.text[:500] if response.text else f"HTTP {response.status_code}"

