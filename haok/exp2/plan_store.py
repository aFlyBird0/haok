from typing import List

from bson import ObjectId

from haok.action_to_module.module_define import example_fibonacci
from haok.exp2.plan_extract_agent import convert_json_to_string
from haok.module.module import Module, Param
from haok.database.mongo import default_db
from haok.config.config import Database
from haok.vector.vector import get_vector_collection,save_plan_vector, get_similar_plan_vectors
class PlanStore:
    """
    save/load plans from mongodb
    """

    def __init__(self):
        self.db = default_db
        # mongo 存 module 详情
        self.col = self.db.get_collection(Database.plan_collection)
        # 向量数据库
        self.vector_collection = get_vector_collection(Database.plan_collection)

    def add(self, plan):
        task = plan['task']
        steps = plan['steps']
        if not steps or len(steps) == 0:
            return "No steps provided"
        # insert if name not exist
        if not self.col.find_one({"task": task}):
            res = self.col.insert_one(plan)
            print(f"已经成功添加plan：{task}: {steps}")
            save_plan_vector(collection=self.vector_collection, task=task, id=str(res.inserted_id))
            return res.inserted_id

    def add_batch(self, plans):
        ids = []
        for plan in plans:
            ids.append(self.add(plan))
        return ids

    def get_by_id(self, id: str):
        col = self.col.find_one({"_id": id})
        return col

    def list_by_filter(self, **filter) -> List[Module]:
        cols = self.col.find(filter)

        # for col in cols:
        #     print(col)

        return cols

    def list(self):
        return self.col.find()

    def list_by_ids(self, ids: List[str]):
        idsObj = [ObjectId(id) for id in ids]
        return self.list_by_filter(_id = {"$in": idsObj})

    def find_similar_module(self, task: str):
        similar_modules = get_similar_plan_vectors(collection=self.vector_collection, task=task)
        ids = similar_modules["ids"][0]
        distances = similar_modules["distances"][0]
        documents = similar_modules["documents"][0]
        if len(ids) == 0:
            return []
        # 筛选出距离小于阈值的id
        max_distance = 4
        selected_ids = []
        for i in range(0, len(ids)):
            if distances[i] <= max_distance:
                selected_ids.append(ids[i])

        return self.list_by_ids(selected_ids)

default_plan_store = PlanStore()


if __name__ == '__main__':
#     p = PlanStore()
#     plans = [
#   {
#     "task": "find and take a tomato",
#     "steps": [
#       "go to countertop 1",
#       "take tomato 1 from countertop 1"
#     ]
#   },
#   {
#     "task": "cool the tomato with the fridge",
#     "steps": [
#       "go to fridge 1",
#       "cool tomato 1 with fridge 1"
#     ]
#   },
#   {
#     "task": "put the tomato in the microwave",
#     "steps": [
#       "go to microwave 1",
#       "open microwave 1",
#       "put tomato 1 in/on microwave 1"
#     ]
#   }
# ]
#     ids = p.add_batch(plans)
#
#     print(ids)
#
#     for plan in p.list():
#         print(plan)

    p = default_plan_store

    print(p.find_similar_module("put a clean tomato in countertop."))
    print(convert_json_to_string(default_plan_store.find_similar_module(task="put a clean plate in countertop.")))