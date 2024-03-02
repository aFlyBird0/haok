import asyncio
import logging
from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Sequence,
                    TypeVar, Union)
from uuid import UUID

import langchain_core.outputs
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import AsyncCallbackHandler, BaseCallbackHandler

from haok.loggers.logs import setup_logger

total_token_usage = 0
class MyCustomSyncHandler(BaseCallbackHandler):
    logger = setup_logger(name="MyCustomSyncHandler", level=logging.INFO)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        logging.debug(f"同步回调被调用: token: {token}")
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        # print("\nLLM调用开始....\n")
        # self.logger.info(f"\nprompts: {prompts}")
        # for prompt in prompts:
        #     self.logger.info(f"prompt: {prompt}")

    def on_llm_end(self, response: langchain_core.outputs.LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        # print("\nLLM调用结束....\n")
        # self.logger.info(f"llm_result: {response}")
        # self.logger.info(f"last llm message: {response.generations[-1][-1].text}")
        # self.logger.info(f"llm id info: run_id: {kwargs['run_id']}, parent_run_id: {kwargs['parent_run_id']}")
        # print("Hi! I just woke up. Your llm is ending")
        # usage = response.llm_output["token_usage"]
        # # print(usage)
        # global total_token_usage
        # total_token_usage += usage["total_tokens"]
        #
        # print(f"total_token_usage: {total_token_usage/1000}k")

    def on_agent_action(
            self,
            action: AgentAction,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        """Run on agent action."""

        action_infos = {
            "action": action,
            "run_id": run_id,
            "parent_run_id": parent_run_id,
        }
        # self.logger.info(f"next_action_infos: {action_infos}")

    def on_agent_finish(
            self,
            finish: AgentFinish,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        """Run on agent end."""

        finish_infos = {
            "finish": finish,
            "run_id": run_id,
            "parent_run_id": parent_run_id,
        }

        # self.logger.info(f"finish_infos: {finish_infos}")