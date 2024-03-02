# 将组件重写成Python代码的Agent

from typing import Any, Tuple

from langchain_community.callbacks import get_openai_callback
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from langchain_core.agents import AgentAction, AgentFinish
from langchain_experimental.tools import PythonREPLTool

# Internal Imports
from haok.callbacks.callback import MyCustomSyncHandler
from haok.module.module import Module
from haok.llm.openai import OpenAIConfig
from haok.loggers.logs import setup_logger

from .example import example_cn
from .output_parser import ArgsAndCodeOutputParser
from .prompt import SYSTEM_PROMPT_CN_TEMPLATE, USER_PROMPT_CN_TEMPLATE

# Third-party Library Imports

# todo: 改成继承 BaseAgent
class ActionToPythonAgent():

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.logger = setup_logger()
        self.agent = self.setup_agent(OpenAIConfig.defaultLLM())

    @property
    def _chain_type(self):
        return "ActionToPythonAgent"

    def python_args_from_action(self, code, log, origin_main_task: str) -> Tuple[Module, float, float, float]:
        with get_openai_callback() as cb:
            agent_finish: AgentFinish = self.agent.invoke(
                {
                    "code": code,
                    "task_log": log,
                    "origin_main_task": origin_main_task,
                },
                {
                    "callbacks": [MyCustomSyncHandler()]
                }
            )
        total_tokens_k = round(cb.total_tokens / 1000, 3)
        prompt_tokens_k = round(cb.prompt_tokens / 1000, 3)
        completion_tokens_k = round(cb.completion_tokens / 1000, 3)

        module = agent_finish.return_values["module"]

        return module, total_tokens_k, prompt_tokens_k, completion_tokens_k

    def setup_agent(self, llm):
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_CN_TEMPLATE),
                HumanMessagePromptTemplate.from_template(USER_PROMPT_CN_TEMPLATE)
            ]
        )
        prompt = prompt.partial(
            **example_cn,
        )

        agent = prompt | llm | ArgsAndCodeOutputParser()

        return agent


action_to_python_agent = ActionToPythonAgent()

if __name__ == '__main__':
    code_to_test = """
def is_prime():
    number = 10
    if number <= 1.
        return False
    for i in range(2, int(number**0.5) + 1): if number % i == 0: return False.
        if number % i == 0: if number <= 1: return False
            return False
    return True

number_to_check = 100

if is_prime(number_to_check): print(f"{number_to_check}")
    print(f"{number_to_check} is prime")
print(f"{number_to_check} is prime")
    print(f"{number_to_check} is not prime")
"""
    task_log = "I need to check if a number is prime, and print out the result."
    origin_main_task = "find 100th prime number"
    action = AgentAction(
        tool_input=code_to_test,
        log=task_log,
        tool=PythonREPLTool().name,
    )
    args = action_to_python_agent.python_args_from_action(action, origin_main_task=origin_main_task)

    print(f"name: {args.name}")
    print(f"description: {args.description}")
    # print(f"args: {args.args}")
    print(f"params: {args.params}")
    print(f"code: {args.code}")
