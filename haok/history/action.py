from typing import List

from bson import ObjectId

from haok.config.config import Database
from haok.database.mongo import default_db


class ActionHistory:
    def __init__(self, tool: str, tool_input, log: str, task: str, result: str, id: str = None,
                 transformed: bool = False):
        self.tool = tool
        self.tool_input = tool_input
        self.log = log
        self.task = task
        self.result = result
        self.id = id
        self.transformed = transformed

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "tool": self.tool,
            "tool_input": self.tool_input,
            "log": self.log,
            "task": self.task,
            "result": self.result,
            "transformed": self.transformed
        }


class ActionHistoryStore:
    def __init__(self):
        self.db = default_db
        self.col = self.db.get_collection(Database.action_history_collection)

    def save(self, action_history: ActionHistory):
        action_history_dict = action_history.to_dict()
        del action_history_dict["_id"]
        result = self.col.insert_one(action_history_dict)
        return str(result.inserted_id)

    def mark_as_transformed(self, id: str):
        query = {"_id": ObjectId(id)}
        update = {"$set": {"transformed": True}}
        self.col.update_one(query, update)

    def list_all(self, transformed: bool = None) -> List[ActionHistory]:
        if transformed is not None:
            cursor = self.col.find({"transformed": transformed})
        else:
            cursor = self.col.find()

        action_histories = []
        for document in cursor:
            action_histories.append(ActionHistory(
                tool=document.get('tool'),
                tool_input=document.get('tool_input'),
                log=document.get('log'),
                task=document.get('task'),
                result=document.get('result'),
                id=str(document.get('_id')),
                transformed=document.get('transformed', False)
            ))
        return action_histories

    def get_by_id(self, id: str) -> ActionHistory:
        query = {"_id": ObjectId(id)}
        result = self.col.find_one(query)
        return ActionHistory(
            tool=result.get('tool'),
            tool_input = result.get('tool_input'),
            log = result.get('log'),
            task = result.get('task'),
            result = result.get('result'),
            id = str(result.get('_id')),
            transformed = result.get('transformed', False)
        )

default_action_history_store = ActionHistoryStore()
