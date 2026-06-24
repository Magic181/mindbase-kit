# RAG架构设计

## 概述

RAG (Retrieval-Augmented Generation) 是AI Notebook的核心能力，通过检索用户文档来增强LLM的回答质量。

## 架构流程

```
用户问题
    │
    ▼
┌─────────────────┐
│  Query Process  │  问题预处理、意图识别
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embedding     │  将问题转换为向量
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Search   │  向量相似度检索
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Rerank       │  重排序、过滤
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Context Building │  构建上下文
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generate   │  生成回答
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Citation     │  标注引用来源
└─────────────────┘
```

## 模块设计

### Embedding Service

```python
class EmbeddingService:
    """向量化服务"""
    
    def embed_text(self, text: str) -> List[float]:
        """单条文本向量化"""
        
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量文本向量化"""
```

支持的模型：
- OpenAI text-embedding-3-small/large
- 本地模型 (Ollama)

### Vector Store

```python
class VectorStore:
    """向量存储接口"""
    
    def insert(self, id: str, vector: List[float], metadata: dict):
        """插入向量"""
        
    def search(self, vector: List[float], top_k: int = 10) -> List[SearchResult]:
        """相似度搜索"""
        
    def delete(self, ids: List[str]):
        """删除向量"""
```

支持的存储：
- Milvus (生产)
- ChromaDB (开发)

### Reranker

```python
class Reranker:
    """重排序服务"""
    
    def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """重排序"""
```

### RAG Pipeline

```python
class RAGPipeline:
    """RAG流水线"""
    
    def __init__(self, embedding, vector_store, reranker, llm):
        self.embedding = embedding
        self.vector_store = vector_store
        self.reranker = reranker
        self.llm = llm
    
    async def query(self, question: str, notebook_id: int) -> RAGResponse:
        """执行RAG查询"""
        # 1. 问题向量化
        # 2. 向量检索
        # 3. 重排序
        # 4. 构建上下文
        # 5. LLM生成
        # 6. 标注引用
```

## 检索策略

### 基础检索

- 向量相似度搜索
- Top K结果

### 混合检索

- 向量搜索 + 关键词搜索
- 分数融合

### 多路召回

- 语义检索
- 关键词检索
- 元数据过滤

## 分块策略

### 固定大小分块

- 块大小：512 tokens
- 重叠：50 tokens

### 语义分块

- 按段落/章节分割
- 保持语义完整性

### 递归分块

- 先按大结构分割
- 再按小结构细分

## 引用标注

### 引用格式

```json
{
  "text": "回答内容",
  "citations": [
    {
      "chunk_id": "doc_1_chunk_5",
      "document_name": "论文.pdf",
      "page": 12,
      "content": "原文片段..."
    }
  ]
}
```

### 引用链接

- 支持点击跳转到原文位置
- 高亮显示引用内容