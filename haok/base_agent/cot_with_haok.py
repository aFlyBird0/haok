import json
import sys
from io import StringIO

from langchain.output_parsers import JsonOutputToolsParser
from langchain_community.utilities.python import PythonREPL
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import Tool
from langchain_core.utils.function_calling import convert_to_openai_tool

from haok.action_to_module.module_gen import default_module_generator
from haok.interpreter.python_tool import PythonTool
from haok.llm.openai import OpenAIConfig
from haok.module.module_store import default_module_store


def get_custom_python_tool():
    return PythonTool()

def get_module_tools(task):
    modules = default_module_store.find_similar_module(task=task)

    tools = [default_module_generator.from_python_args(module) for module in modules]

    return tools

def CoT_with_haok(question: str, task_prefix, example):
    # task_prefix += "You must use python tool to solve this question."
    examples = [example]
    example_prompt = PromptTemplate(
        # input_variables=["question", "answer"], template="Here is one example, you should make sure that the format your your answer is same with example. Example: \nQuestion: " + task_prefix + "{question}\n{answer}"
        input_variables = ["question", "answer"], template = "Example: \nQuestion: " + task_prefix + "{question}\n{answer}"
    )
    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        suffix="Here is your task, Please make sure the result has the same format of Example:\nQuestion: " + task_prefix + "{input}",
        input_variables=["input"],
    )
    output_parser = JsonOutputToolsParser()

    tool_origin = get_module_tools(question)[0]
    tool_name = tool_origin.name
    tool = convert_to_openai_tool(tool_origin)

    # 把所有的参数改成必填
    # params = tool['function']['parameters']
    # properties = params['properties']
    # required = list(properties.keys())
    # params['required'] = required
    # tool['function']['parameters'] = params

    # print("tool", tool)
    # print(json.dumps(tool, indent=2))
    llm = OpenAIConfig.defaultLLM().bind_tools([tool], tool_choice=tool_name)
    # llm = OpenAIConfig.defaultLLM().bind_tools([tool])
    # llm = OpenAIConfig.defaultLLM()
    chain = (
            {"input": RunnablePassthrough()}
            | prompt
            | llm
            | output_parser
    )

    output = chain.invoke(question)

    python_args = output[0]['args']

    print(python_args)

    return tool_origin.run(python_args).strip()