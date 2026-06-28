import logging
import os
from dataclasses import dataclass

from .models import Conversation
from .models import MessageRole
from .rag import (
    Citation,
    DeepSeekError,
    build_prompt,
    call_deepseek_chat,
    retrieve_citations,
    strip_inline_source_markers,
)
from .search_modes import SEARCH_MODE_WEB, uses_local_retrieval, uses_web_search
from .web_search import WebResult, WebSearchError, search_web

logger = logging.getLogger(__name__)

AI_FAILURE_MESSAGE = "回答生成失败，请稍后重试，或检查 AI 服务配置。"
WEB_SEARCH_DEGRADED_MESSAGE = "联网搜索失败，已基于本地资料回答。"
WEB_ONLY_SEARCH_DEGRADED_MESSAGE = "联网搜索失败，已基于模型通用能力回答。"


@dataclass(frozen=True)
class AssistantDraft:
    content: str
    citations: list[Citation]
    web_results: list[WebResult]


@dataclass(frozen=True)
class AssistantContext:
    messages: list[dict]
    citations: list[Citation]
    web_results: list[WebResult]
    degraded_message: str


def generate_assistant_draft(
    conversation: Conversation,
    content: str,
    search_mode: str,
    history_messages: list | None = None,
) -> AssistantDraft:
    try:
        context = prepare_assistant_context(
            conversation=conversation,
            content=content,
            search_mode=search_mode,
            history_messages=history_messages,
        )
        answer = call_deepseek_chat(context.messages)
        answer = strip_inline_source_markers(answer)
        if context.degraded_message:
            answer = f"{context.degraded_message}\n\n{answer}"
    except DeepSeekError as exc:
        logger.exception("Failed to generate chat response for conversation %s", conversation.id)
        answer = getattr(exc, "user_message", AI_FAILURE_MESSAGE)
        context = AssistantContext(messages=[], citations=[], web_results=[], degraded_message='')
    except Exception:
        logger.exception("Unexpected chat response failure for conversation %s", conversation.id)
        answer = AI_FAILURE_MESSAGE
        context = AssistantContext(messages=[], citations=[], web_results=[], degraded_message='')

    return AssistantDraft(content=answer, citations=context.citations, web_results=context.web_results)


def prepare_assistant_context(
    conversation: Conversation,
    content: str,
    search_mode: str,
    history_messages: list | None = None,
) -> AssistantContext:
    citations: list[Citation] = []
    web_results: list[WebResult] = []
    web_search_degraded = False

    top_k = int(os.getenv("RAG_TOP_K", "5"))
    max_ctx = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "8000"))
    history_messages = history_messages or []
    local_query = _build_local_query(content, history_messages)

    if uses_local_retrieval(search_mode) and _should_use_local_retrieval(content, history_messages):
        citations = retrieve_citations(conversation.notebook_id, local_query, top_k=top_k)

    if uses_web_search(search_mode):
        try:
            web_results = search_web(content)
        except WebSearchError:
            logger.warning(
                "Web search failed for conversation %s",
                conversation.id,
                exc_info=True,
            )
            web_search_degraded = True

    messages = build_prompt(
        content,
        citations,
        max_context_chars=max_ctx,
        web_results=web_results,
        history=_build_prompt_history(history_messages),
    )

    degraded_message = _web_search_degraded_message(search_mode) if web_search_degraded else ''
    return AssistantContext(
        messages=messages,
        citations=citations,
        web_results=web_results,
        degraded_message=degraded_message,
    )


def build_citation_payload(
    citations: list[Citation],
    web_results: list[WebResult],
) -> list[dict]:
    return [
        {
            "source_type": "document",
            "document_id": citation.document_id,
            "document_name": citation.document_name,
            "chunk_id": citation.chunk_id,
            "chunk_text": citation.chunk_text,
            "position": citation.position,
            "document_source_type": citation.source_type,
            "metadata": citation.metadata,
        }
        for citation in citations
    ] + [
        {
            "source_type": "web",
            "title": result.title,
            "url": result.url,
            "content": result.content,
            "position": result.position,
        }
        for result in web_results
    ]


def _web_search_degraded_message(search_mode: str) -> str:
    if search_mode == SEARCH_MODE_WEB:
        return WEB_ONLY_SEARCH_DEGRADED_MESSAGE
    return WEB_SEARCH_DEGRADED_MESSAGE


def _build_local_query(content: str, history_messages: list) -> str:
    user_context = [
        msg.content.strip()
        for msg in history_messages
        if msg.role == MessageRole.USER and msg.content.strip()
    ]
    return "\n".join([*user_context[-3:], content])


def _should_use_local_retrieval(content: str, history_messages: list) -> bool:
    text = _normalize_query_text(content)
    if not text:
        return False

    if _has_explicit_local_signal(text):
        return True

    if _is_general_assistant_question(text):
        return False

    recent_user_text = '\n'.join(
        _normalize_query_text(msg.content)
        for msg in history_messages[-3:]
        if msg.role == MessageRole.USER and msg.content.strip()
    )
    return _has_task_signal(text) and _has_explicit_local_signal(recent_user_text)


def _normalize_query_text(content: str) -> str:
    return content.strip().lower()


def _has_explicit_local_signal(text: str) -> bool:
    local_terms = (
        '文档',
        '资料',
        '文件',
        '笔记',
        'notebook',
        '论文',
        '报告',
        '正文',
        '图片',
        '表格',
        '截图',
        '上传',
        '这份',
        '这篇',
        '里面',
        '内容',
        '引用',
        '来源',
        '实验',
        '项目',
        '代码',
        '系统',
        '流程',
        '章节',
        '目录',
        '第',
        '页',
    )
    return any(term in text for term in local_terms)


def _has_task_signal(text: str) -> bool:
    task_terms = (
        '总结',
        '概括',
        '分析',
        '评分',
        '打分',
        '修改',
        '润色',
        '改进',
        '建议',
        '继续',
        '再说',
        '接着',
        '现在',
        '这次',
        '呢',
    )
    return any(term in text for term in task_terms)


def _is_general_assistant_question(text: str) -> bool:
    identity_terms = (
        '你是什么模型',
        '你是啥模型',
        '你用的什么模型',
        '你使用什么模型',
        '你基于什么模型',
        '什么大模型',
        '底层模型',
        '你是谁',
        '你是什么',
        '介绍一下你',
        '自我介绍',
        '你能做什么',
        '你的能力',
    )
    return any(term in text for term in identity_terms)


def _build_prompt_history(history_messages: list) -> list[dict[str, str]]:
    return [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages[-6:]
        if msg.role in {MessageRole.USER, MessageRole.ASSISTANT}
    ]
