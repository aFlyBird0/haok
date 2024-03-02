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

from haok.interpreter.python_tool import PythonTool
from haok.llm.openai import OpenAIConfig

def execute_python_code(code):
    print(code)
    try:
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        exec(code)
        output = new_stdout.getvalue()
        sys.stdout = old_stdout  # 恢复原始的 stdout
        return output
    except Exception as e:
        return f"An error occurred: {e}"

def get_langchain_python_tool():
    tool = Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...). You must use print(...) at last to show me the result`.",
        func=PythonREPL().run
    )
    tool = convert_to_openai_tool(tool)

    return tool

def get_custom_python_tool():
    return PythonTool()

# 最后一行加print
def add_print_to_last_line(input_str):
    lines = input_str.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():  # 找到最后一个非空行
            if not lines[i].lstrip().startswith('print'):
                first_non_whitespace_index = len(lines[i]) - len(lines[i].lstrip())
                lines[i] = lines[i][:first_non_whitespace_index] + f"print({lines[i].rstrip()[first_non_whitespace_index:]})"
            break
    return '\n'.join(lines)

def CoT_with_tool(question: str, task_prefix, example):
    # task_prefix += "You must use python tool to solve this question."
    examples = [example]
    example_prompt = PromptTemplate(
        # input_variables=["question", "answer"], template="Here is one example, you should make sure that the format your your answer is same with example. Example: \nQuestion: " + task_prefix + "{question}\n{answer}"
        input_variables = ["question", "answer"], template = "Example: \nQuestion: " + task_prefix + "{question}\nAnswer: {answer}"
    )
    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        suffix="Here is your task, Please make sure the result has the same format of example。\nQuestion:"+ task_prefix+ "{input}",
        input_variables=["input"],
    )

    # print(prompt.format(input=question))
    # print('q:' + question)
    output_parser = JsonOutputToolsParser()

    tool = convert_to_openai_tool(get_custom_python_tool())

    # print("tool", tool)
    # print(json.dumps(tool, indent=2))
    llm = OpenAIConfig.defaultLLM().bind_tools([tool], tool_choice="python")
    chain = (
            {"input": RunnablePassthrough()}
            | prompt
            | llm
            | output_parser
    )

    output = chain.invoke(question)

    python_args = output[0]['args']
    code = python_args["code"]
    code = add_print_to_last_line(code)
    # dependencies = python_args["dependencies"]
    dependencies = []

    # return PythonTool().run({"code": code, "dependencies": dependencies}).strip()
    return PythonTool()._run(code, dependencies).strip()
    # return execute_python_code(code)

    # code = output[0]['args']['__arg1']
    # print(code)
    # return PythonREPL().run(code).strip()