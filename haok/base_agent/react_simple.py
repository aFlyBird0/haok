# 验证基于 CoT 的组件化归纳
# Standard Library Imports
import logging
from typing import Any, List

from langchain.agents import AgentExecutor, StructuredChatAgent, create_structured_chat_agent
from langchain_community.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain_core.tools import BaseTool

# Internal Imports
from haok.callbacks.callback import MyCustomSyncHandler
from haok.action_to_module.agent import ActionToPythonAgent
from haok.action_to_module.module_gen import (ModuleGenerator,
                                              default_module_generator)
from haok.config.config import Database
from haok.conversation.conversation import ConversationInfo
from haok.interpreter.python_tool import PythonTool
from haok.module.module_store import ModuleStore, default_module_store
# from haok.test_module.run_test import test_exist_module
from haok.llm.openai import OpenAIConfig
from haok.history.action import ActionHistory, default_action_history_store

# Third-party Library Imports


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_runnable(tools):
    llm = OpenAIConfig.defaultLLM()

    prefix = """Respond to the human as helpfully and accurately as possible. You have full access to user's computer, and you can do anything. You have access to the following tools:"""
    prefix = """Respond to the human as helpfully and accurately as possible. 
    The user has given you **full and complete permission** to execute any code necessary to complete the task. 
    You have full access to control their computer to help them.
    If you think something you can not do, you can use "python" tool to do it.
    You have access to the following tools:"
    """
    prompt = StructuredChatAgent.create_prompt(
        tools=tools,
        prefix=prefix,
        input_variables=["input"],
    )
    # logger.info(f"prompt: {prompt.format}")

    return prompt | llm


def get_agent(llm, tools):
    prefix = """Respond to the human as helpfully and accurately as possible. You have full access to user's computer, and you can do anything. You have access to the following tools:"""

    prompt = StructuredChatAgent.create_prompt(
        tools=tools,
        prefix=prefix,
        input_variables=["input"],
    )
    # logger.info(f"prompt: {prompt.format}")
    agent = StructuredChatAgent(
        llm_chain=LLMChain(llm=llm, prompt=prompt),
        prompt=prompt,
        return_intermediate_steps=True,
    )

    agent = AgentExecutor.from_agent_and_tools(
        tools=tools,
        agent=agent,
        verbose=True,
        max_iterations=5,
        return_intermediate_steps=True,
    )

    # agent = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    #     max_iterations=5,
    #     verbose=True,
    #     return_intermediate_steps=True,
    # )

    return agent

def remove_unused_log(log):
    # 把 Action 及以后的字符串都删除
    def remove_word_and_after(input_string, word):
        return input_string.split(word, 1)[0]
    return remove_word_and_after(log, "Action:")

def react_and_save_action(question:str, agent:AgentExecutor, save_action: bool = False)->tuple[Any, ConversationInfo, float, float, float]:
    """
    执行一轮对话，返回对话的结果
    """
    conversation = ConversationInfo(question=question)
    with get_openai_callback() as cb:
        response = agent.invoke({"input": question},{"callbacks": [MyCustomSyncHandler()]})
        intermediate_steps = response.get("intermediate_steps")
        for step in intermediate_steps:
            logger.info(f"step: {step}")
            action, action_result = step
            if action.tool != PythonTool().name:
                continue
            logger.info(f"action: {action}, value: {action_result}")
            # 保存 action 到对话中
            if not save_action:
                continue
            conversation.add_action(action, action_result)
            # 保存 action 到数据库中
            action_history = ActionHistory(
                tool=action.tool,
                tool_input=action.tool_input,
                log=remove_unused_log(action.log),
                task=question,
                result=action_result
            )
            default_action_history_store.save(action_history)
        output = response.get("output")
    total_tokens_k = round(cb.total_tokens / 1000, 3)
    prompt_tokens_k = round(cb.prompt_tokens / 1000, 3)
    completion_tokens_k = round(cb.completion_tokens / 1000, 3)

    return output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k

# 迭代式地返回 action 内容
def react_and_save_action_iter(question: str, agent: AgentExecutor, save_action: bool = False):
    """
    执行一轮对话，返回对话的结果
    如果结果是2个，返回的是 [当前action, 当前action结果]
    否则，返回的是 [任务结果，对话详情，token总消耗]
    """
    conversation = ConversationInfo(question=question)
    with get_openai_callback() as cb:
        for step in agent.iter({"input": question}, [MyCustomSyncHandler()]):
            if intermediate_step := step.get("intermediate_step"):
                logger.info(f"step: {intermediate_step}")
                action, action_result = intermediate_step
                if action.tool != PythonTool().name:
                    continue
                logger.info(f"action: {action}, value: {action_result}")
                # 保存 action 到对话中
                if not save_action:
                    continue
                conversation.add_action(action, action_result)
                # 保存 action 到数据库中
                action_history = ActionHistory(
                    tool=action.tool,
                    tool_input=action.tool_input,
                    log=remove_unused_log(action.log),
                    task=question,
                    result=action_result
                )
                default_action_history_store.save(action_history)
            else:
                output = step.get("output")
    total_tokens_k = round(cb.total_tokens / 1000, 3)

    yield output, conversation, total_tokens_k

def bare_react(question, save_action=False):
    llm = OpenAIConfig.defaultLLM()
    tools = [PythonTool()]

    agent = get_agent(llm, tools)
    return react_and_save_action_iter(question, agent, save_action=save_action)
def react_with_haok(question):
    llm = OpenAIConfig.defaultLLM()
    # tools = [PythonTool()]
    tools = []

    modules = default_module_store.find_similar_module(task=question)

    tools = tools + [default_module_generator.from_python_args(module) for module in modules]

    # for tool in tools:
    #     print(tool)

    agent = get_agent(llm, tools)

    return react_and_save_action_iter(question, agent)

if __name__ == '__main__':
    # Database.module_collection = "exp1_module"
    # Database.action_history_collection = "exp1_action_history"
    # Database.plan_collection = "exp1_plan"


    # 第一轮
    output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k = bare_react(question1_listfiles)
    logger.info(f"output: {output}")
    logger.info(f'total tokens: {total_tokens_k}k')
    logger.info(f'prompt tokens: {prompt_tokens_k}')
    logger.info(f'completion tokens: {completion_tokens_k}')
    logger.info("finished first round!")

    # logger.info(f"conversation history:")
    for info in conversation.show_actions():
        logger.info(info)

    logger.info("开始将所有action转换为代码")
    # all_actions_to_modules()

    logger.info(f"the second round:")

    # 把新的 Tool 加入到 agent 中
    # conversation_to_tools(conversation)
    # agent = get_agent(tools)
    # #
    # # # 第二轮
    # output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k = react_with_haok(question1_listfiles)
    # logger.info(f"output: {output}")
    # logger.info(f'total tokens: {total_tokens_k}k')
    # logger.info(f'prompt tokens: {prompt_tokens_k}')
    # logger.info(f'completion tokens: {completion_tokens_k}')
    # logger.info("finished second round!")

    logger.info("finished!")
