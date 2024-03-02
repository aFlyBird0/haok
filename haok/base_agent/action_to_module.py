import logging

from haok.action_to_module.agent import ActionToPythonAgent
from haok.history.action import default_action_history_store, ActionHistory
from haok.module.module_store import default_module_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def action_to_module(action: ActionHistory):
    # Ask user if they want to continue
    logger.info(
        f"action: {action.tool}, log: {action.log}, tool_input: {action.tool_input}, tool_result: {action.result}")
    # _continue = input("Would you transform the action above into a new module (Y/n)?:\n")
    # if _continue != "Y":
    #     return
    module_args, total_tokens_k, prompt_tokens_k, completion_tokens_k = ActionToPythonAgent().python_args_from_action(
        action.tool_input, action.log, action.task)
    # new_module_tool = default_module_generator.from_python_args(module_args)

    default_module_store.add(module_args)
    # 标记这个action已经转换为了模块
    default_action_history_store.mark_as_transformed(action.id)
    print(
        f'action_to_module_cost: total_tokens_k: {total_tokens_k}, prompt_tokens_k: {prompt_tokens_k}, completion_tokens_k: {completion_tokens_k}')


def action_id_to_module(action_id: str):
    action = default_action_history_store.get_by_id(action_id)
    action_to_module(action)


def all_actions_to_modules():
    actions = default_action_history_store.list_all(transformed=False)
    for action in actions:
        action_to_module(action)