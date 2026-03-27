from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from typing import List, Dict, Any
from app.core.config import settings


class MilvusStore:
    """Milvus向量存储服务"""
    
    def __init__(self):
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self._connect()
    
    def _connect(self):
        """连接到Milvus"""
        connections.connect(
            alias="default",
            host=self.host,
            port=self.port
        )
    
    def create_collection(self, collection_name: str, dimension: int = 384) -> Collection:
        """创建集合"""
        # 检查集合是否已存在
        if utility.has_collection(collection_name):
            return Collection(collection_name)
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
        ]
        
        # 创建Schema
        schema = CollectionSchema(
            fields=fields,
            description=f"Knowledge base collection: {collection_name}"
        )
        
        # 创建集合
        collection = Collection(
            name=collection_name,
            schema=schema
        )
        
        # 创建索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        return collection
    
    def insert_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        """插入文档片段"""
        collection = Collection(collection_name)
        
        # 准备数据
        ids = [f"{chunk['doc_id']}_{chunk['chunk_index']}" for chunk in chunks]
        doc_ids = [chunk['doc_id'] for chunk in chunks]
        chunk_indices = [chunk['chunk_index'] for chunk in chunks]
        chunk_texts = [chunk['text'] for chunk in chunks]
        
        # 插入数据
        collection.insert([
            ids,
            doc_ids,
            chunk_indices,
            chunk_texts,
            embeddings
        ])
        
        # 刷新以确保数据被持久化
        collection.flush()
    
    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索相似的文档片段"""
        collection = Collection(collection_name)
        collection.load()
        
        # 搜索参数
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # 执行搜索
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["doc_id", "chunk_index", "chunk_text"]
        )
        
        # 格式化结果
        formatted_results = []
        for result in results[0]:
            formatted_results.append({
                "doc_id": result.entity.get("doc_id"),
                "chunk_index": result.entity.get("chunk_index"),
                "chunk_text": result.entity.get("chunk_text"),
                "score": result.score
            })
        
        return formatted_results
    
    def delete_by_doc_id(self, collection_name: str, doc_id: str):
        """根据文档ID删除所有相关片段"""
        collection = Collection(collection_name)
        
        # 查询要删除的ID
        results = collection.query(
            expr=f"doc_id == '{doc_id}'",
            output_fields=["id"]
        )
        
        if results:
            ids_to_delete = [result["id"] for result in results]
            collection.delete(ids_to_delete)
    
    def drop_collection(self, collection_name: str):
        """删除集合"""
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)