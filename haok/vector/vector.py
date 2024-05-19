import typing

import chromadb
from chromadb.utils import embedding_functions

from haok.config.config import Database
from haok.config.settings import get_settings

def get_vector_collection(collection_name)->chromadb.Collection:
    persist_dir = '.chromadb'
    # 这里有个历史遗留，当时没有考虑到 ChatModel 和 EmbeddingModel 可能来自不同供应商
    # 所以 EmbeddingModel 这里就写死 OpenAI 了
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_base="https://api.nextapi.fun/v1",
        api_key="ak-nyH5E1ka6oFKqRzxxqAooqcKSGCrk38mMgvU1DTqgOgRyTUQ",
        model_name="text-embedding-3-small",
    )
    client = chromadb.PersistentClient(persist_dir)
    collection = client.get_or_create_collection(collection_name, embedding_function=openai_ef)
    return collection

def save_module_vector(collection:chromadb.Collection, module_name, id):
    collection.add(documents=[module_name], ids=[id])

# 保存数据增强后的任务规划，也就是多个任务描述信息，对应一个任务
def save_plan_vector_with_data_augmented(collection:chromadb.Collection, tasks: typing.List[str], source_task_id: str):
    metadata = [{"source_task_id": source_task_id} for _ in tasks]
    collection.add(documents=tasks, metadatas=metadata, ids=tasks)

# 保存数据规划，不进行数据增强
def save_plan_vector(collection:chromadb.Collection, task, id):
    collection.add(documents=[task], ids=[id])

def get_similar_module_vectors(collection:chromadb.Collection, task, n_results=1):
    res = collection.query(query_texts=[task], n_results=n_results)
    # print(res)
    # ids = res['ids']
    # if ids == None or len(ids) == 0:
    #     return []
    # return ids
    return res

def get_similar_plan_vectors_with_data_augmented(collection:chromadb, task:str, n_results=3):
    res = collection.query(query_texts=[task], n_results=n_results)
    return res

def get_similar_plan_vectors(collection:chromadb.Collection, task:str, n_results=10):
    res = collection.query(query_texts=[task], n_results=n_results)
    return res

if __name__ == '__main__':
    collection = get_vector_collection(Database.module_collection)
    collection.add(documents=['鸡兔同笼问题', '算出前5个质数', '质数'], ids=['1', '3', '4'])

    res = get_similar_module_vectors(collection, '质数')
    print(collection.get())
    print(res)