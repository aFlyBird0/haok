from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Param(BaseModel):
    name: str = Field(description="The name of the param")
    param_type: str = Field(description="the type, only support string, integer, float, boolean, array",
                                        # ", object",
                            # enum=["str", "int", "float", "bool", "list", "dict", "object"])
                            enum = ["str", "int", "float", "bool", "list"])
    default: Optional[Any] = Field(description="The default value of the param",default=None)
    description: str = Field(description="The description of the param")
    required: bool = Field(description="Whether the param is required", default=True)

    def to_json_schema(self):
        json_schema = {
            "type": self.param_type,
            "description": self.description,
        }
        if self.default:
            json_schema["default"] = self.default
        return json_schema


class Module(BaseModel):
    name: str = Field(description="The name of the module")
    description: str = Field(description="The description of the module")
    tags: List[str] = Field(default_factory=List[str], description="用于描述函数的功能/用途/特性/分类等等",
                            example=["math", "fibonacci"])
    code: str = Field(description="The code of the module, now only support Python")
    # args: dict[str,str] = Field(default_factory=dict[str,str], description="The args of the module", example={"a": "1", "b": "2"})
    params: List[Param] = Field(default_factory=List[Param], description="The params of the module")
    author: str = Field(default="admin", description="The author of the module")
    # id: str = ""
    # kind: str = "Python"
    dependencies: List[str] = Field(description="需要使用pip安装的python包", default_factory=list[str])

    id: str = Field(description="The id of the module, only used for database", default="")

    def to_json_schema_without_code(self):
        return Module.schema()["properties"]

    def schema_only_params(self)->BaseModel:
        parameters = {
            "type": "object",
            "properties": {},
            "name": "params",
        }
        if self.params:
            parameters["properties"] = {param.name: param.to_json_schema() for param in self.params}
            parameters["required"] = [param.name for param in self.params if param.required]

        return BaseModel(**parameters)

    def to_dict(self):
        return self.dict()

    def to_dict_only_core_field(self):
        return self.dict(exclude={"code", "id", "author"})

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls.parse_obj(json_dict)


if __name__ == '__main__':
    print(Module.schema_json(indent=4))
