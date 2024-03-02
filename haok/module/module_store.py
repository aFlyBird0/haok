from typing import List

from bson import ObjectId

from haok.action_to_module.module_define import example_fibonacci
from haok.module.module import Module, Param
from haok.database.mongo import default_db
from haok.config.config import Database
from haok.vector.vector import get_vector_collection,save_module_vector, get_similar_module_vectors

class ModuleStore:
    """
    save/load modules from mongodb
    """

    def __init__(self):
        self.modules = []
        self.db = default_db
        # mongo 存 module 详情
        self.col = self.db.get_collection(Database.module_collection)
        # 向量数据库
        self.vector_collection = get_vector_collection(Database.module_collection)

    def add(self, module: Module):
        # insert if name not exist
        if not self.col.find_one({"name": module.name, "author": module.author}):
            module_dict = module.to_dict()
            del module_dict["id"]
            res = self.col.insert_one(module_dict)
            print(f"已经成功添加模块：{module.author}/{module.name}")
            save_module_vector(collection=self.vector_collection, module_name=module.name, id=str(res.inserted_id))
            return res.inserted_id

    def get_by_id(self, id: str) -> Module:
        col = self.col.find_one({"_id": id})
        if col:
            return self._col_to_mod(col)

    def list_by_filter(self, **filter) -> List[Module]:
        cols = self.col.find(filter)

        # for col in cols:
        #     print(col)

        return [self._col_to_mod(col) for col in cols if col]

    def list_by_ids(self, ids: List[str]) -> List[Module]:
        idsObj = [ObjectId(id) for id in ids]
        return self.list_by_filter(_id = {"$in": idsObj})

    def list(self) -> List[Module]:
        return self.list_by_filter()

    def list_by_name(self, module_name: str) -> List[Module]:
        return self.list_by_filter(name=module_name)

    def list_by_author(self, module_author: str) -> List[Module]:
        return self.list_by_filter(author=module_author)

    def list_by_tags_or(self, tags_list_or: list) -> List[Module]:
        # tag in module_tags
        tags_filter = {"tags": {"$in": tags_list_or}}
        return self.list_by_filter(**tags_filter)

    def list_by_tags_and(self, tags_list_and: list) -> List[Module]:
        # tag in module_tags
        tags_filter = {"tags": {"$all": tags_list_and}}
        return self.list_by_filter(**tags_filter)

    def list_by_name_and_tags_and(self, module_name: str, tags_list_and: list) -> List[Module]:
        # tag in module_tags and module_name contain module_name
        regex = f".*{module_name}.*"
        tags_filter = {"name": {"$regex": regex}}
        if len(tags_list_and) > 0:
            tags_filter["tags"] = {"$all": tags_list_and}
        return self.list_by_filter(**tags_filter)

    def list_by_name_and_tags_or(self, module_name: str, tags_list_or: list) -> List[Module]:
        regex = f".*{module_name}.*"
        tags_filter = {"name": {"$regex": regex}}
        if len(tags_list_or) > 0:
            tags_filter["tags"] = {"$in": tags_list_or}
        return self.list_by_filter(**tags_filter)

    # def list_by_kind(self, kind: str) -> List[Module]:
    #     modules = []
    #     for module in self.modules:
    #         if module.kind == kind:
    #             modules.append(module)
    #     return modules

    def delete_by_id(self, id: str):
        self.col.delete_one({"_id": id})

    def _col_to_mod(self, col) -> Module:
        mod = Module(**col)
        mod.id = str(col["_id"])
        return mod

    def print_all(self, logger):
        for module in self.modules:
            module.print(logger)

    def find_similar_module(self, task: str):
        similar_modules = get_similar_module_vectors(collection=self.vector_collection, task=task)
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

default_module_store = ModuleStore()

if __name__ == '__main__':
    m = ModuleStore()
    test_module = Module(
        name="考研分数排名",
        description="xxx",
        author="admin",
        tags=["test", "math"],
        code="print('hello world')",
        # args={"number": "int"},
        params=[
            Param(name="number", param_type="int", default=10, description="number to calculate"),
        ]
    )
    m.add(test_module)

    m.find_similar_module("分数排名")

if __name__ == "__main__2":
    m = ModuleStore()
    python_test_module = Module(
        name="test_py_math2",
        description="xxx",
        author="admin",
        tags=["test", "math"],
        code="print('hello world')",
        # args={"number": "int"},
        params=[
            Param(name="number", param_type="int", default=10, description="number to calculate"),
        ]
    )

    m.add(example_fibonacci())
    id = m.add(python_test_module)
    print(f"id inserted {id}")
    print(f"get last inserted: {m.get_by_id(id)}")

    for v in m.list_by_filter():
        print(vars(v))

    print("tags or")
    for v in m.list_by_tags_or(["test", "math"]):
        print(vars(v))

    print("tags and")
    for v in m.list_by_tags_and(["fibonacci", "math"]):
        print(vars(v))

    m.delete_by_id(id)

    for v in m.list():
        print(vars(v))
