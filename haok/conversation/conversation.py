from typing import Dict, List, Tuple

from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage


class ConversationInfo:
    # question: str
    # actions: List[Tuple[AgentAction, str]] = None    # action, result
    # # actions_maps: Dict[str, AgentAction] = None  # nodeID->Action
    # messages: List[BaseMessage]

    def __init__(self, question: str):
        self.question:str = question
        self.actions: List[Tuple[AgentAction, str]] = []
        self.actions_maps = {}
        self.messages = []

    def add_action(self, action: AgentAction, result: str):
        self.actions.append((action, result))

    def show_actions(self):
        return [(action[0].log, action[1]) for action in self.actions]

    def get_actions(self):
        return self.actions

    def show_messages(self):
        return [message.content for message in self.messages]
