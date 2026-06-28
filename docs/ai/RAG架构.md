# RAG 架构

> 最后更新：2026-06-28

## 概述

AI Notebook 当前 RAG 是轻量但结构感知的实现：文档解析产生结构化片段，本地检索按问题意图召回图片、表格、代码、标题等证据，随后进行重排、去重和引用诊断；Chat 还支持 Tavily 联网搜索和混合搜索。

当前未接入 embedding 或向量数据库。向量检索、语义召回和外部 reranker 属于后续升级项。

## 总体流程

```
用户问题
  → 搜索模式判断(local/web/hybrid)
  → 本地检索：关键词召回 + 结构意图增强
  → 联网搜索：Tavily 可选
  → 证据重排、去重、多样性选择
  → 构建回答 Prompt
  → DeepSeek 生成
  → 返回回答 + citations
```

## 文档入库

```
TXT / MD / PDF / DOCX
  → parse_file_blocks
  → paragraph / heading / table / code / page blocks
  → chunk_blocks
  → DocumentChunk(metadata.source_type)
  → extract_assets
  → OCR blocks(image_ocr)
  → Vision blocks(image_caption)
```

### 支持的片段类型

| source_type | 来源 |
|-------------|------|
| paragraph | 普通段落 |
| heading | Markdown/DOCX 标题 |
| table | Markdown/DOCX 表格 |
| code | Markdown 代码块 |
| page | PDF 页文本 |
| image_ocr | 图片 OCR 文本 |
| image_caption | 视觉模型生成的图片描述 |

## 本地检索

模块：`backend/apps/chat/rag.py`

### 1. 问题 token 化

- 去除常见无效词，例如“帮我”“总结”“这个”。
- 中文长词会拆成短片段，提高基础命中率。
- Broad query 会触发更宽松的最近文档召回。

### 2. 意图识别

当前识别四类问题意图：

| 意图 | 典型词 |
|------|--------|
| image | 图片、截图、流程图、架构图、图中、diagram |
| table | 表格、字段、列、行、统计、dataset |
| code | 代码、函数、接口、脚本、报错、api |
| heading | 标题、章节、目录、结构、outline |

### 3. 结构加权

检索会给匹配意图的片段类型加权。例如：

- 图片问题优先 `image_caption` 和 `image_ocr`。
- 表格问题优先 `table`。
- 代码问题优先 `code`。
- 结构/目录问题优先 `heading`。

### 4. 证据重排

每个候选片段会生成：

- `retrieval_score`: 综合命中、结构类型、位置等因素的分数。
- `retrieval_reason`: 给前端和调试使用的命中说明。
- `evidence_key`: 用于去重，避免同一图片/同一段重复占满 Top K。

最终会按分数和多样性选择 Top K。

## 联网搜索

模块：`backend/apps/chat/web_search.py`

| search_mode | 行为 |
|-------------|------|
| local | 只使用 Notebook 内已解析文档 |
| web | 只使用 Tavily 搜索结果 |
| hybrid | 同时使用本地文档和联网结果 |

未配置 `TAVILY_API_KEY` 时，web/hybrid 会返回友好降级，不会让聊天接口崩溃。

## 回答策略

模块：`backend/apps/chat/services.py`

Prompt 会根据证据情况调整回答策略：

- 有足够证据时，要求基于引用回答。
- 证据不足时，明确说明缺口，避免编造。
- 命中图片、表格、代码时，要求按对应结构解释。
- 联网搜索结果会以 `[W1]`、`[W2]` 等来源加入上下文。

## Citations

文档 citation 示例：

```json
{
  "source_type": "document",
  "document_id": 1,
  "document_name": "report.pdf",
  "chunk_id": 12,
  "chunk_text": "原文片段...",
  "position": 3,
  "metadata": {
    "source_type": "image_caption",
    "page": 2,
    "asset_id": 4,
    "asset_name": "diagram.png",
    "vision_provider": "zhipu",
    "vision_model": "glm-4.6v-flashx",
    "retrieval_score": 38,
    "retrieval_reason": "匹配图片意图，命中流程图关键词"
  }
}
```

网页 citation 示例：

```json
{
  "source_type": "web",
  "title": "网页标题",
  "url": "https://example.com",
  "content": "网页摘要...",
  "position": 1
}
```

## 故障与降级

| 场景 | 行为 |
|------|------|
| DeepSeek 未配置 Key | 返回 AI 配置不完整提示 |
| DeepSeek 认证失败 | 返回认证失败提示 |
| Tavily 未配置或失败 | web/hybrid 返回搜索降级说明 |
| OCR 失败 | 文档仍可完成，文档卡片展示 OCR 错误 |
| 视觉模型繁忙 | 自动重试，可配置 fallback，文档卡片展示友好错误 |
| 本地没有命中证据 | 回答会说明未找到足够资料 |

## 后续升级

- Embedding 召回。
- 向量数据库：Milvus、ChromaDB 或 pgvector。
- Cross-encoder reranker。
- 文档定位高亮。
- 更细粒度的图片区域、表格单元格和代码符号引用。
