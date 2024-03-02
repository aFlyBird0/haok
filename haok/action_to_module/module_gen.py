import logging
from typing import Callable, List, Type, Union

# Internal Imports
from langchain_core.agents import AgentAction
from langchain_core.tools import BaseTool, StructuredTool
from langchain_experimental.tools import PythonREPLTool
# Third-party Library Imports
from pydantic import BaseModel, create_model, Field
from pydantic.fields import FieldInfo

from haok.action_to_module.agent import ActionToPythonAgent
from haok.action_to_module.module_define import example_fibonacci
from haok.interpreter.python import PythonInterpreter
from haok.module.module import Module, Param
from haok.module.module_store import ModuleStore, default_module_store
from haok.loggers.logs import setup_logger


class ModuleGenerator:
    def __init__(self, logger: logging.Logger = None, ):
        if logger is None:
            self.logger = setup_logger()

        self.agent = ActionToPythonAgent()

    def all_from_db(self, store: ModuleStore = default_module_store) -> List[StructuredTool]:
        return [self.from_python_args(args) for args in store.list()]

    def from_action(self, action: AgentAction, question: str = "") -> Union[BaseTool, None]:
        if action.tool == PythonREPLTool().name:
            return self.from_python_action(action, question)

        self.logger.error(f"only support PythonREPLTool, but got {action.tool}")
        return None

    def from_python_action(self, action: AgentAction, question: str = "") -> Union[BaseTool, None]:
        module: Module = self.agent.python_args_from_action(action.tool_input, action.log, question)[0]

        # self.store.add(args)

        return self.from_python_args(module)

    def example_fibonacci_tool(self) -> StructuredTool:
        # args = PythonModule(
        #     name=example_args_extracted_json["name"],
        #     description=example_args_extracted_json["description"],
        #     code=example_refactored_code,
        #     args=example_args_extracted_json["args"],
        #     tags=example_args_extracted_json["tags"]
        # )
        return self.from_python_args(example_fibonacci())

    def from_python_args(self, module: Module) -> StructuredTool:
        name = module.name
        description = module.description
        code = module.code
        # args_schema = args_schema.schema_only_params()

        def params_to_base_model(params: List[Param])-> Type[BaseModel]:
            fields = {}
            for param in params:
                if param.name == "swaps_sequence":
                    field_info = (param.param_type, FieldInfo(description=param.description))
                else:
                    field_info = (param.param_type, ...)
                fields[param.name] = field_info

            return create_model("args", **fields)

        # def params_to_base_model(params: List[Param])-> Type[BaseModel]:
        #     fields = {}
        #     for param in params:
        #         fields[param.name] = (param.param_type, ...)
        #
        #     return create_model("args", **fields)

        def funcWrapper(code: str) -> Callable:
            # 上层调用的时候，tool_input 是字典，对应 **kwargs
            def func(*args, **kwargs):
                # print(f"\n正在执行Python模块化代码:\n{code}")
                # 将所有的参数解包，传入代码中，实现形参和实参的动态绑定
                return PythonInterpreter().run(code, **kwargs)
                # return PythonREPL(_globals=globals(), _locals=kwargs).run(code)
                # return exec(code)

            return func

        tool = StructuredTool(
            name=name,
            description=description,
            args_schema=params_to_base_model(module.params),
            func=funcWrapper(code)
        )

        return tool

    # 将形如 {"tool_input": {"type": "string"}} 的形参字典转换为 pydantic 模型
    # 注：后面临时改成了更简单的形式，形如 {"tool_input": "string"}
    # def _create_args_schema(self, args_dict: dict, model_name: str = "DynamicModel") -> Type[BaseModel]:
    #     model_fields = {}
    #
    #     # self.logger.info(f"start to create args schema, args_dict: {args_dict}")
    #
    #     for arg_name, arg_info in args_dict.items():
    #         # arg_type = arg_info["type"]
    #         arg_type = arg_info
    #         model_fields[arg_name] = (eval(arg_type), ...)
    #
    #     dynamic_model = create_model(model_name, **model_fields)
    #     # dynamic_model = type(model_name, (BaseModel,), model_fields)
    #     return dynamic_model


default_module_generator = ModuleGenerator()

if __name__ == '__main__':
    module = example_fibonacci()
    # schema = module.schema_only_params()
    # print(schema.schema_json(indent=2))
    tool = default_module_generator.from_python_args(module)
    print(tool.name)
    print(tool.description)
    print(tool.args_schema.schema_json(indent=2))
    print(tool.func)
