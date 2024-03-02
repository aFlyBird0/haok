from pydantic import BaseModel, Field

from haok.module.module import Module, Param

from .example import example_args_extracted_json, example_refactored_code


# @deprecated(version='0.1.0', reason="Use Module instead")
class PythonModule(BaseModel):
    name: str
    description: str
    tags: list
    code: str
    args: dict[str,str] = Field(default_factory=dict[str,str], description="The args of the module", example={"a": "1", "b": "2"})
    author: str = Field(default="admin", description="The author of the module")
    id: str = ""
    kind: str = "Python"
    dependencies: list = []

    def print(self, logger):
        logger.info(f"重构后的Python代码信息，name：{self.name}, description: {self.description}, args: {self.args}")
        logger.info(f"重构后的Python代码内容：\n{self.code}")

    def to_dict(self):
        return self.dict()

    def to_json(self):
        return self.json(indent=4)

def example_fibonacci() -> Module:
    params = [
        Param(name="number", param_type="int", description="The nth number of the fibonacci sequence", required=True)
    ]
    return Module(
        name=example_args_extracted_json["name"],
        description=example_args_extracted_json["description"],
        code=example_refactored_code,
        params=params,
        tags=example_args_extracted_json["tags"],
        dependencies=example_args_extracted_json["dependencies"]
    )