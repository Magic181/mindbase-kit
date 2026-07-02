import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any

import requests
from requests import exceptions as request_exceptions
from django.db.models import Q

from apps.documents.models import Document, DocumentChunk, DocumentStatus

from .web_search import WebResult


@dataclass(frozen=True)
class Citation:
    document_id: int
    document_name: str
    chunk_id: int
    chunk_text: str
    position: int
    source_type: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class QueryIntent:
    source_boosts: dict[str, int]
    fallback_source_types: tuple[str, ...]


@dataclass(frozen=True)
class ScoredChunk:
    chunk: DocumentChunk
    score: int
    reason: str
    evidence_key: tuple[Any, ...]


class DeepSeekError(RuntimeError):
    user_message = "AI 服务暂时不可用，请稍后重试。"


class DeepSeekConfigError(DeepSeekError):
    user_message = "AI 服务配置不完整，请检查 DeepSeek API Key。"


class DeepSeekAuthError(DeepSeekError):
    user_message = "AI 服务认证失败，请检查 DeepSeek API Key。"


class DeepSeekRequestError(DeepSeekError):
    user_message = "AI 请求参数无效，请检查模型配置。"


QUERY_STOP_TERMS = {
    '一下',
    '这个',
    '这些',
    '这份',
    '这篇',
    '里面',
    '内容',
    '请问',
    '请你',
    '帮我',
    '根据',
    '基于',
    '总结',
    '概括',
    '归纳',
    '整理',
}

BROAD_CONTEXT_TERMS = {
    '总结',
    '概括',
    '归纳',
    '摘要',
    '梳理',
    '整理',
    '分析',
    '评价',
    '建议',
    '整体',
    '全局',
    '全部',
    '所有',
    '完整',
    '这些',
    '几个',
    '看看',
    '全文',
    '文档',
    '资料',
    '文件',
    '上传',
    '读取',
    '读到',
    '报告',
    '论文',
    'notebook',
    'summarize',
    'summary',
    'overview',
}

SOURCE_INTENT_TERMS = {
    'image': (
        '图片',
        '图像',
        '截图',
        '配图',
        '照片',
        '流程图',
        '架构图',
        '图表',
        '图里',
        '图中',
        '看图',
        'image',
        'picture',
        'screenshot',
        'diagram',
        'chart',
    ),
    'table': (
        '表格',
        '表',
        '清单',
        '字段',
        '列',
        '行',
        '数据',
        '统计',
        'table',
        'sheet',
        'column',
        'row',
        'dataset',
    ),
    'code': (
        '代码',
        '函数',
        '接口',
        '脚本',
        '类',
        '方法',
        '实现',
        '报错',
        'code',
        'function',
        'class',
        'api',
        'script',
        'error',
    ),
    'heading': (
        '标题',
        '章节',
        '目录',
        '小节',
        '结构',
        'heading',
        'section',
        'outline',
    ),
}

SOURCE_TYPE_BOOSTS = {
    'document_overview': {},
    'image_caption': {'image': 14},
    'image_ocr': {'image': 12},
    'table': {'table': 14},
    'code': {'code': 14},
    'heading': {'heading': 8, 'code': 2},
    'paragraph': {'code': 1, 'heading': 1},
    'page': {'image': 1, 'table': 1, 'code': 1, 'heading': 1},
}


def _tokenize(query: str) -> list[str]:
    query = query.strip().lower()
    if not query:
        return []
    tokens = re.split(r'[\s,，.。;；:：!?！？()\[\]{}"“”\'`]+', query)
    terms: list[str] = []
    for token in tokens:
        if len(token) < 2:
            continue
        terms.extend(_expand_search_terms(token))
    return _unique_terms(terms)[:12]


def _expand_search_terms(token: str) -> list[str]:
    if not re.search(r'[\u4e00-\u9fff]', token):
        return [] if token in QUERY_STOP_TERMS else [token]

    cleaned = token
    for term in QUERY_STOP_TERMS:
        cleaned = cleaned.replace(term, ' ')

    terms: list[str] = []
    for segment in re.findall(r'[\u4e00-\u9fffA-Za-z0-9]+', cleaned):
        if len(segment) < 2:
            continue
        if segment not in QUERY_STOP_TERMS:
            terms.append(segment)
        if len(segment) > 4 and re.search(r'[\u4e00-\u9fff]', segment):
            terms.extend(
                segment[index:index + 2]
                for index in range(0, len(segment) - 1)
            )
    return terms


def _unique_terms(terms: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        if term in QUERY_STOP_TERMS or term in seen:
            continue
        seen.add(term)
        unique.append(term)
    return unique


def _is_broad_context_query(query: str) -> bool:
    lowered = query.lower()
    return any(term in lowered for term in BROAD_CONTEXT_TERMS)


def _is_document_availability_query(query: str) -> bool:
    lowered = query.lower()
    direct_terms = (
        '能读到',
        '读得到',
        '读到',
        '没读到',
        '读取到',
        '读取',
        '只读',
        '只读取',
        '看得到',
        '识别到',
    )
    if any(term in lowered for term in direct_terms):
        return True
    has_upload_subject = any(term in lowered for term in ('上传', '文件', '文档', '资料'))
    has_question_signal = any(term in lowered for term in ('能', '吗', '有没有', '是否'))
    has_read_signal = any(term in lowered for term in ('读', '看', '识别'))
    return has_upload_subject and has_question_signal and has_read_signal


def _is_document_inventory_query(query: str) -> bool:
    lowered = query.lower()
    return (
        any(term in lowered for term in ('上传', '我上传', '这些', '全部', '所有'))
        and any(term in lowered for term in ('文件', '文档', '资料', '作业', '论文', '报告', '都', '哪些', '列表'))
    )


def _is_grading_query(query: str) -> bool:
    lowered = query.lower()
    return any(term in lowered for term in ('打分', '评分', '给分', '评估', '预估', '多少分', '扣分', '考核'))


def _is_multi_document_context_query(query: str) -> bool:
    lowered = query.lower()
    subject_terms = (
        '文件',
        '文档',
        '资料',
        '作业',
        '大作业',
        '论文',
        '报告',
        'notebook',
    )
    scope_terms = (
        '整体',
        '全局',
        '全部',
        '所有',
        '完整',
        '这些',
        '几个',
        '上传的',
        '我上传',
        '总结',
        '概括',
        '分析',
        '评价',
        '建议',
        '看看',
        '怎么样',
    )
    return any(term in lowered for term in subject_terms) and any(term in lowered for term in scope_terms)


def _detect_query_intent(query: str) -> QueryIntent:
    lowered = query.lower()
    matched_intents = {
        intent
        for intent, terms in SOURCE_INTENT_TERMS.items()
        if any(term in lowered for term in terms)
    }
    if not matched_intents:
        return QueryIntent(source_boosts={}, fallback_source_types=())

    source_boosts: dict[str, int] = {}
    for source_type, boosts in SOURCE_TYPE_BOOSTS.items():
        score = sum(boost for intent, boost in boosts.items() if intent in matched_intents)
        if score:
            source_boosts[source_type] = score

    fallback_source_types = tuple(
        source_type
        for source_type, _ in sorted(
            source_boosts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    return QueryIntent(
        source_boosts=source_boosts,
        fallback_source_types=fallback_source_types,
    )


def retrieve_citations(notebook_id: int, query: str, top_k: int = 5) -> list[Citation]:
    tokens = _tokenize(query)
    intent = _detect_query_intent(query)
    is_broad_context_query = _is_broad_context_query(query)
    is_document_availability_query = _is_document_availability_query(query)
    is_document_inventory_query = _is_document_inventory_query(query)
    is_grading_query = _is_grading_query(query)
    is_multi_document_context_query = _is_multi_document_context_query(query)
    include_overview_citations = (
        is_document_availability_query
        or is_document_inventory_query
        or is_grading_query
        or (is_multi_document_context_query and top_k >= 6)
    )
    overview_citations = (
        _document_overview_citations(notebook_id, max_docs=min(top_k, max(3, top_k // 3)))
        if include_overview_citations
        else []
    )
    remaining_top_k = max(0, top_k - len(overview_citations))
    if remaining_top_k <= 0:
        return overview_citations[:top_k]

    use_broad_ranking = (
        (is_broad_context_query or is_multi_document_context_query)
        and not intent.fallback_source_types
        and top_k >= 6
    )
    base_qs = DocumentChunk.objects.select_related('document').filter(
        document__notebook_id=notebook_id,
        document__status=DocumentStatus.COMPLETED,
    )
    candidate_limit = max(top_k * 8, top_k)

    chunks: list[DocumentChunk] = []
    if tokens:
        content_q = Q()
        name_q = Q()
        for t in tokens:
            content_q |= Q(content__icontains=t)
            if _is_document_name_token(t):
                name_q |= Q(document__name__icontains=t)
        chunks.extend(base_qs.filter(content_q).order_by('-id')[:candidate_limit])
        if name_q:
            chunks.extend(base_qs.filter(name_q).order_by('-document__created_at', 'position')[:candidate_limit])
    if intent.fallback_source_types:
        chunks.extend(
            base_qs.filter(metadata__source_type__in=intent.fallback_source_types)
            .order_by('-id')[:candidate_limit]
        )
    if is_grading_query:
        chunks.extend(
            base_qs.exclude(metadata__source_type='document_overview')
            .order_by('-document__created_at', 'position')[:candidate_limit * 3]
        )
    elif is_multi_document_context_query:
        chunks.extend(
            base_qs.exclude(metadata__source_type='document_overview')
            .order_by('-document__created_at', 'position')[:candidate_limit * 2]
        )
    if use_broad_ranking:
        chunks.extend(base_qs.order_by('-document__created_at', 'position')[:candidate_limit])

    chunks = _deduplicate_chunks(chunks)
    if not chunks and is_broad_context_query:
        chunks = list(base_qs.order_by('-document__created_at', 'position')[:top_k])
        use_broad_ranking = True

    scored_chunks = _score_chunks(
        chunks=chunks,
        tokens=tokens,
        query=query,
        intent=intent,
        use_broad_ranking=use_broad_ranking,
    )
    if not scored_chunks and is_broad_context_query:
        chunks = list(base_qs.order_by('-document__created_at', 'position')[:remaining_top_k])
        use_broad_ranking = True
        scored_chunks = _score_chunks(
            chunks=chunks,
            tokens=tokens,
            query=query,
            intent=intent,
            use_broad_ranking=use_broad_ranking,
        )
    if is_grading_query or is_multi_document_context_query:
        scored_chunks = _select_balanced_document_chunks(scored_chunks, top_k=remaining_top_k)
    else:
        scored_chunks = _select_diverse_chunks(scored_chunks, top_k=remaining_top_k)

    citations: list[Citation] = [*overview_citations]
    chunk_text_limit = 4000 if is_grading_query else 1200 if is_multi_document_context_query else 500
    for item in scored_chunks:
        c = item.chunk
        doc = c.document
        metadata = {
            **(c.metadata or {}),
            'retrieval_score': item.score,
            'retrieval_reason': item.reason,
        }
        citations.append(
            Citation(
                document_id=doc.id,
                document_name=doc.name,
                chunk_id=c.id,
                chunk_text=c.content[:chunk_text_limit],
                position=c.position,
                source_type=(c.metadata or {}).get('source_type', 'text'),
                metadata=metadata,
            )
        )
    return citations[:top_k]


def _score_chunks(
    chunks: list[DocumentChunk],
    tokens: list[str],
    query: str,
    intent: QueryIntent,
    use_broad_ranking: bool,
) -> list[ScoredChunk]:
    scored: list[ScoredChunk] = []
    for chunk in chunks:
        metadata = chunk.metadata or {}
        source_type = metadata.get('source_type', 'text')
        text = (chunk.content or '').lower()
        token_weight = 1 if use_broad_ranking else 4
        token_hits = sum(text.count(t) for t in tokens) if tokens else 0
        token_score = token_hits * token_weight
        name_score = _document_name_score(query, tokens, chunk.document.name)
        body_score = _body_text_score(query, source_type)
        source_score = intent.source_boosts.get(source_type, 0)
        grading_score = _grading_score(query, chunk.document.name, source_type, chunk.position)
        broad_score = _broad_context_score(chunk) if use_broad_ranking else 0
        score = token_score + name_score + body_score + source_score + grading_score + broad_score
        if score <= 0:
            continue
        scored.append(
            ScoredChunk(
                chunk=chunk,
                score=score,
                reason=_retrieval_reason(token_hits, name_score, body_score, source_score, grading_score, broad_score),
                evidence_key=_evidence_key(chunk),
            )
        )
    scored.sort(key=lambda item: (item.score, -item.chunk.id), reverse=True)
    return scored


def _select_diverse_chunks(scored_chunks: list[ScoredChunk], top_k: int) -> list[ScoredChunk]:
    selected: list[ScoredChunk] = []
    selected_keys: set[tuple[Any, ...]] = set()

    for item in scored_chunks:
        if item.evidence_key in selected_keys:
            continue
        selected.append(item)
        selected_keys.add(item.evidence_key)
        if len(selected) >= top_k:
            return selected

    if len(selected) >= top_k:
        return selected

    selected_ids = {item.chunk.id for item in selected}
    for item in scored_chunks:
        if item.chunk.id in selected_ids:
            continue
        selected.append(item)
        selected_ids.add(item.chunk.id)
        if len(selected) >= top_k:
            break
    return selected


def _select_balanced_document_chunks(scored_chunks: list[ScoredChunk], top_k: int) -> list[ScoredChunk]:
    selected: list[ScoredChunk] = []
    selected_ids: set[int] = set()
    per_document_counts: dict[int, int] = {}
    first_pass_limit = max(1, min(3, top_k // 3 or 1))

    for item in scored_chunks:
        document_id = item.chunk.document_id
        if item.chunk.id in selected_ids:
            continue
        if per_document_counts.get(document_id, 0) >= first_pass_limit:
            continue
        selected.append(item)
        selected_ids.add(item.chunk.id)
        per_document_counts[document_id] = per_document_counts.get(document_id, 0) + 1
        if len(selected) >= top_k:
            return selected

    for item in scored_chunks:
        if item.chunk.id in selected_ids:
            continue
        selected.append(item)
        selected_ids.add(item.chunk.id)
        if len(selected) >= top_k:
            break
    return selected


def _document_name_score(query: str, tokens: list[str], document_name: str) -> int:
    name = document_name.lower()
    score = 0
    for token in tokens:
        if not _is_document_name_token(token):
            continue
        if token in name:
            score += 8

    query_terms = ('大论文', '论文', '报告', '考核说明', '说明')
    for term in query_terms:
        if term in query and term in document_name:
            score += 12
    return min(score, 36)


def _is_document_name_token(token: str) -> bool:
    if token in QUERY_STOP_TERMS:
        return False
    if token in {'大论', '论文', '考核', '说明', '正文'}:
        return True
    return len(token) >= 3


def _body_text_score(query: str, source_type: str) -> int:
    if not any(term in query for term in ('正文', '全文', '文档内容', '报告内容')):
        return 0
    if source_type in {'mixed', 'paragraph', 'page', 'table'}:
        return 28
    if source_type in {'image_ocr', 'image_caption'}:
        return -28
    return 0


def _grading_score(query: str, document_name: str, source_type: str, position: int) -> int:
    if not _is_grading_query(query):
        return 0

    score = 0
    if _is_rubric_document(document_name):
        score += 18
    else:
        score += 44

    if source_type in {'mixed', 'paragraph', 'table'}:
        score += 18
    elif source_type in {'image_ocr', 'image_caption'}:
        score += 8
    elif source_type == 'page':
        score += 10

    score += max(0, 8 - min(position or 0, 8))
    return score


def _is_rubric_document(document_name: str) -> bool:
    return any(term in document_name for term in ('考核说明', '评分标准', '要求说明'))


def _retrieval_reason(
    token_hits: int,
    name_score: int,
    body_score: int,
    source_score: int,
    grading_score: int,
    broad_score: int,
) -> str:
    reasons = []
    if token_hits:
        reasons.append('keyword_match')
    if name_score:
        reasons.append('document_name')
    if body_score > 0:
        reasons.append('body_text')
    if source_score:
        reasons.append('source_intent')
    if grading_score:
        reasons.append('grading_context')
    if broad_score:
        reasons.append('document_context')
    return '+'.join(reasons) if reasons else 'unknown'


def _evidence_key(chunk: DocumentChunk) -> tuple[Any, ...]:
    metadata = chunk.metadata or {}
    source_type = metadata.get('source_type', 'text')
    document_id = chunk.document_id

    if source_type in {'image_ocr', 'image_caption'}:
        asset_id = metadata.get('asset_id')
        if asset_id is not None:
            return (document_id, 'image', asset_id)
        asset_position = metadata.get('asset_position')
        if asset_position is not None:
            return (document_id, 'image', asset_position)

    if source_type == 'table':
        table_index = metadata.get('table_index')
        if table_index is not None:
            return (document_id, 'table', table_index)

    page = metadata.get('page')
    if page is not None:
        return (document_id, source_type, page, chunk.position // 3)

    return (document_id, source_type, chunk.position // 2)


def _deduplicate_chunks(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    seen: set[int] = set()
    unique: list[DocumentChunk] = []
    for chunk in chunks:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        unique.append(chunk)
    return unique


def _broad_context_score(chunk: DocumentChunk) -> int:
    position = chunk.position or 0
    return max(0, 8 - min(position, 8))


def _document_overview_citations(notebook_id: int, max_docs: int) -> list[Citation]:
    documents = Document.objects.filter(
        notebook_id=notebook_id,
        status=DocumentStatus.COMPLETED,
    ).order_by('-created_at')[:max_docs]

    citations: list[Citation] = []
    for document in documents:
        chunks = list(document.chunks.order_by('position'))
        if not chunks:
            continue
        first_chunk = chunks[0]
        citations.append(
            Citation(
                document_id=document.id,
                document_name=document.name,
                chunk_id=first_chunk.id,
                chunk_text=_document_overview_text(document, chunks),
                position=first_chunk.position,
                source_type='document_overview',
                metadata={
                    'source_type': 'document_overview',
                    'retrieval_score': 100,
                    'retrieval_reason': 'document_parse_overview',
                },
            )
        )
    return citations


def _document_overview_text(document: Document, chunks: list[DocumentChunk]) -> str:
    source_counts: dict[str, int] = {}
    pages: set[Any] = set()
    for chunk in chunks:
        metadata = chunk.metadata or {}
        source_type = metadata.get('source_type', 'text')
        source_counts[source_type] = source_counts.get(source_type, 0) + 1
        if metadata.get('page') is not None:
            pages.add(metadata['page'])

    lines = [
        f'文档解析概况：{document.name}',
        f'文件类型：{document.file_type.upper()}',
        f'解析片段数：{len(chunks)}',
        f'内容类型：{_format_source_counts(source_counts)}',
    ]
    if pages:
        lines.append(f'覆盖页码：{min(pages)}-{max(pages)}，共 {len(pages)} 页')

    sample = _document_overview_sample(chunks)
    if sample:
        lines.append(f'正文示例：{sample}')
    return '\n'.join(lines)


def _format_source_counts(source_counts: dict[str, int]) -> str:
    return '、'.join(
        f'{_source_label(source_type)} {count} 个'
        for source_type, count in sorted(source_counts.items())
    )


def _document_overview_sample(chunks: list[DocumentChunk]) -> str:
    preferred_types = {'mixed', 'paragraph', 'page', 'table'}
    for chunk in chunks:
        metadata = chunk.metadata or {}
        source_type = metadata.get('source_type', 'text')
        text = ' '.join((chunk.content or '').split())
        if source_type in preferred_types and chunk.position > 1 and len(text) >= 80:
            return text[:220]
    for chunk in chunks:
        text = ' '.join((chunk.content or '').split())
        if len(text) >= 40:
            return text[:220]
    return ''


def build_prompt(
    query: str,
    citations: list[Citation],
    max_context_chars: int = 8000,
    web_results: list[WebResult] | None = None,
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    context_blocks: list[str] = []
    remaining = max_context_chars
    for idx, c in enumerate(citations, start=1):
        source_label = _source_label(c.source_type)
        block = (
            f"资料来源 {idx}：{c.document_name}（chunk#{c.position}，{source_label}）\n"
            f"{c.chunk_text}"
        ).strip()
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
            f"网页来源 {idx}：{result.title}\n"
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
        "你是 AI Notebook 的资料协作助手，语气自然、主动、专业。\n"
        "回答规则：\n"
        "- 先直接回答用户的问题，再补充依据和限制；不要一上来要求用户重新提供资料。\n"
        "- 只要资料片段不为空，就表示已经读取到 Notebook 的可解析内容，禁止说“没有读取到上传内容”。\n"
        "- 如果资料片段包含“文档概况”，先用它判断文件是否解析完整；不要只凭某个封面片段断定正文不存在。\n"
        "- 如果文档概况列出了用户的大作业、个人作业或其他已上传文件，禁止说这些文件没有上传或没有读到。\n"
        "- 用户要求打分、评分或评估时，要同时使用评分标准和作业内容；如果证据不足，只能标注“基于当前片段暂估”，不能把缺失片段当成不存在。\n"
        "- 对资料型问题，优先基于资料片段回答，但不要在正文里输出 [1]、[W1]、【W1】 等编号标记；来源会由界面单独展示。\n"
        "- 如果片段只覆盖部分内容，要明确说“基于当前检索到的片段”，并给出可推断结论。\n"
        "- 如果用户问图片、流程图、截图或图表，优先使用图片描述、OCR、表格和附近文字回答；没有图片描述时也要基于已解析内容继续给出可用判断，避免输出“看不到像素内容”等技术限制话术。\n"
        "- 若提供了网页搜索结果，可以结合网页内容回答，但不要把网页来源编号写进正文。\n"
        "- 对问候、助手能力、模型身份、产品使用方式等通用问题，可以直接自然回答。\n"
        "- 回答要像可用的产品助手：具体、少兜圈子、少模板话。\n"
    )

    context = "\n\n".join(context_blocks) if context_blocks else ""
    source_summary = _source_summary(citations, web_results)
    answer_strategy = _answer_strategy(query, citations, web_results)
    if context:
        user = (
            f"用户问题：{query}\n\n"
            f"资料状态：{source_summary}\n\n"
            f"回答策略：{answer_strategy}\n\n"
            f"资料片段：\n{context}"
        )
    else:
        user = (
            f"用户问题：{query}\n\n"
            f"资料状态：未检索到可用资料片段。\n\n"
            f"回答策略：{answer_strategy}\n\n"
            f"资料片段：无"
        )

    messages = [{"role": "system", "content": system}]
    for item in history or []:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        messages.append({"role": role, "content": content[:1000]})
    messages.append({"role": "user", "content": user})
    return messages


def _source_label(source_type: str) -> str:
    labels = {
        'document_overview': '文档概况',
        'paragraph': '正文段落',
        'heading': '标题',
        'page': '页面文本',
        'table': '表格',
        'code': '代码块',
        'image_ocr': '图片 OCR',
        'image_caption': '图片描述',
        'mixed': '混合文本',
        'text': '文本',
    }
    return labels.get(source_type, source_type or '文本')


def _answer_strategy(
    query: str,
    citations: list[Citation],
    web_results: list[WebResult],
) -> str:
    has_local_context = bool(citations)
    has_web_context = bool(web_results)
    source_types = {citation.source_type for citation in citations}
    strategies = [
        '先给结论，再给依据；不要在正文里输出来源编号，也不要把资料状态复述成模板话。',
        '证据不足时明确缺口，但继续给出基于现有证据的可用判断或下一步建议。',
    ]

    if not has_local_context and not has_web_context:
        strategies.append(
            '如果这是通用问题，可以直接回答；如果是在问 Notebook 内容，就说明本次没有命中相关片段，建议换更具体的问题或重新解析资料。'
        )

    if _has_image_intent(query):
        image_sources = {'image_ocr', 'image_caption'} & source_types
        if image_sources:
            strategies.append('用户在问图片/图表；已检索到图片 OCR 或图片描述，可以把它作为图片解析结果来回答。')
        elif has_local_context:
            strategies.append(
                '用户在问图片/图表；本次没有命中图片描述时，不要强调技术限制，直接基于已检索到的文字、表格或附近说明给出可用分析。'
            )

    if 'table' in source_types:
        strategies.append('包含表格证据时，优先提取字段、行列关系、数字和状态，不要只做泛泛概括。')

    if 'code' in source_types:
        strategies.append('包含代码证据时，说明函数、接口、参数、返回值或执行流程，避免只翻译代码表面文字。')

    return ' '.join(strategies)


def strip_inline_source_markers(text: str, *, strip_partial: bool = False) -> str:
    text = re.sub(r'(?:\s*(?:\[(?:W|w)?\d+\]|【(?:W|w)?\d+】))+', '', text)
    if strip_partial:
        text = re.sub(r'\s*(?:\[(?:W|w)?\d*|【(?:W|w)?\d*)$', '', text)
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', text)
    text = re.sub(r'\s+([，。；：！？,.!?])', r'\1', text)
    return text


def _has_image_intent(query: str) -> bool:
    lowered = query.lower()
    return any(term in lowered for term in SOURCE_INTENT_TERMS['image'])


def _source_summary(citations: list[Citation], web_results: list[WebResult]) -> str:
    parts = []
    if citations:
        source_counts: dict[str, int] = {}
        for citation in citations:
            source_counts[citation.source_type] = source_counts.get(citation.source_type, 0) + 1
        detail = '、'.join(
            f"{_source_label(source_type)} {count} 个"
            for source_type, count in source_counts.items()
        )
        parts.append(f"已检索到 Notebook 片段 {len(citations)} 个（{detail}）")
    if web_results:
        parts.append(f"已检索到网页结果 {len(web_results)} 个")
    return '；'.join(parts) if parts else '未检索到可用资料片段'


def call_deepseek_chat(messages: list[dict[str, Any]]) -> str:
    config = _deepseek_config()

    data = {
        "model": config["model"],
        "messages": messages,
        "temperature": 0.2,
    }

    resp = _post_with_retries(
        f"{config['base_url']}/chat/completions",
        headers=config["headers"],
        json=data,
        timeout=config["timeout"],
        retries=config["retries"],
        backoff=config["backoff"],
    )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def stream_deepseek_chat(messages: list[dict[str, Any]]):
    config = _deepseek_config()
    data = {
        "model": config["model"],
        "messages": messages,
        "temperature": 0.2,
        "stream": True,
    }
    response = _post_stream_with_retries(
        f"{config['base_url']}/chat/completions",
        headers=config["headers"],
        json=data,
        timeout=config["timeout"],
        retries=config["retries"],
        backoff=config["backoff"],
    )
    try:
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            if not line.startswith('data:'):
                continue
            payload = line.removeprefix('data:').strip()
            if payload == '[DONE]':
                break
            try:
                event = json.loads(payload)
            except ValueError:
                continue
            choices = event.get('choices') or []
            if not choices:
                continue
            delta = choices[0].get('delta') or {}
            content = delta.get('content') or ''
            if content:
                yield content
    finally:
        response.close()


def _deepseek_config() -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise DeepSeekConfigError("DEEPSEEK_API_KEY 未配置")

    return {
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/"),
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "retries": int(os.getenv("DEEPSEEK_MAX_RETRIES", "2")),
        "backoff": float(os.getenv("DEEPSEEK_RETRY_BACKOFF_SECONDS", "0.2")),
        "timeout": float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60")),
        "headers": {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    }


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


def _post_stream_with_retries(
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
                stream=True,
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

    raise DeepSeekError(str(last_error or "DeepSeek stream request failed"))


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

