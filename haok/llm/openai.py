from langchain_openai import ChatOpenAI
from haok.config.settings import get_settings

openai_api_key = get_settings().llm.api_key
openai_api_base = get_settings().llm.api_base
default_model = get_settings().llm.default_model

class OpenAIConfig:

    openai_params = {
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base
    }

    @staticmethod
    def chatglm4():
        return ChatOpenAI(
        model_name="glm-4",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4",
        openai_api_key="eyJhbGciOiJIUzI1NiIsInNpZ25fdHlwZSI6IlNJR04iLCJ0eXAiOiJKV1QifQ.eyJhcGlfa2V5IjoiNjI5NzcxMjc5MzA3NTU4YzVlODI3MTdmYmUzMWIyZGMiLCJleHAiOjE3MTY3OTk4Nzk3ODYsInRpbWVzdGFtcCI6MTcwOTAyMzg3OTc4Nn0.83ZPAoa_ZC7dvvs7J7p_dtHP9eXc3sea8e2OOtszjWw",
        streaming=False,
    )

    @staticmethod
    def openai():
        # os.environ["OPENAI_API_KEY"] = OpenAIConfig.openai_api_key
        return ChatOpenAI(
            # model_name="gpt-3.5-turbo-1106",
            model_name=default_model,
            # model_name="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base,
            temperature=0,
        )

    @staticmethod
    def openai4():
        # os.environ["OPENAI_API_KEY"] = OpenAIConfig.openai_api_key
        return ChatOpenAI(
            # model_name="gpt-3.5-turbo-1106",
            model_name="gpt-4-0125-preview",
            # model_name="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base,
            temperature=0,
        )

    @staticmethod
    def openai_with_params(model: str=default_model, temperature: float=0.0):
        return ChatOpenAI(
            model_name=model,
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base,
            temperature=temperature,
        )

    @staticmethod
    def defaultLLM():
        # return OpenAIConfig.chatglm4()
        return OpenAIConfig.openai()

    @staticmethod
    def llm_with_params(model: str=default_model, temperature: float=0.0):
        # 如果model含有gpt
        if "gpt" in model:
            return ChatOpenAI(
                model_name=model,
                openai_api_key=openai_api_key,
                openai_api_base=openai_api_base,
                temperature=temperature,
            )
        elif "glm" in model:
            return OpenAIConfig.chatglm4()
        else:
            return OpenAIConfig.defaultLLM()