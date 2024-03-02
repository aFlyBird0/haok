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

question1_fibonacci = "Calculate the 10th Fibonacci number, add it to the square root of 600, and round the result to two decimal places. Give me the final result number rather than just code."
question2_fibonacci = "Calculate the 5th Fibonacci number, add it to the square root of 20, and round the result to two decimal places. Give me the final result number rather than just code."

question1_prime = "Calculate the first prime number greater than 20. Give me the final result number rather than just code."
question2_prime = "Calculate the first prime number greater than 30. Give me the final result number rather than just code."

question1_listfiles = "list files in current directory."
question2_listfile = "list files in current directory, and reorder them by alphabetical order, and tell me the result."

question1_read_file_op = "please summarize README.md in current directory, and save the result as README_summary.md."
question2_read_file_op = "please enrich README.md in current directory, and save the result as README_enrich.md."

question1_numpy = "please use numpy to generate a rand vector in the dimension of 10. And run it to get the result."
question2_numpy = "please use numpy to generate a rand matrix in the dimension of 10*10. And run it to get the result."

question1_pdf = "please list all files in current directory, and save the file names as a pdf file."
question2_pdf = "please list all files in current directory, and save the file names as a pdf file."

question1_patent = "告诉我50后面的第20个质数"
question2_patent = "告诉我60后面的第2个质数"

question1, question2 = question1_patent, question2_patent


def get_all_tools(module_gen: ModuleGenerator = default_module_generator, store: ModuleStore = default_module_store) -> List[BaseTool]:
    # 默认的工具
    tools: list[BaseTool] = [PythonTool()]
    # 从数据库中读取组件
    tools = tools + module_gen.all_from_db(store=store)
    return tools


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


def react_and_conversation(question:str, agent:AgentExecutor)->tuple[Any, ConversationInfo, float]:
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
            logger.info(f"action: {action}, value: {action_result}")
            conversation.add_action(action, action_result)
        output = response.get("output")
    total_tokens_k = round(cb.total_tokens / 1000, 3)

    return output, conversation, total_tokens_k

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
def react_and_conversation_iter(question: str, agent: AgentExecutor):
    """
    执行一轮对话，返回对话的结果
    如果结果是2个，返回的是 [当前action, 当前action结果]
    否则，返回的是 [任务结果，对话详情，token总消耗]
    """
    conversation = ConversationInfo(question=question)
    with get_openai_callback() as cb:
        for step in agent.iter({"input": question}, [MyCustomSyncHandler()]):
            if intermediate_step := step.get("intermediate_step"):
                action, action_result = intermediate_step[0]
                logger.info(f"action: {action}, value: {action_result}")
                conversation.add_action(action, action_result)
                yield action, action_result
            else:
                output = step.get("output")
    total_tokens_k = round(cb.total_tokens / 1000, 3)

    yield output, conversation, total_tokens_k

def bare_react(question, save_action=False):
    llm = OpenAIConfig.defaultLLM()
    tools = [PythonTool()]

    agent = get_agent(llm, tools)
    return react_and_save_action(question, agent, save_action=save_action)
def react_with_haok(question):
    llm = OpenAIConfig.defaultLLM()
    # tools = [PythonTool()]
    tools = []

    modules = default_module_store.find_similar_module(task=question)

    tools = tools + [default_module_generator.from_python_args(module) for module in modules]

    # for tool in tools:
    #     print(tool)

    agent = get_agent(llm, tools)

    return react_and_save_action(question, agent)

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
