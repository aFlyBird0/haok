from functools import lru_cache

from pydantic import BaseSettings, Field


class CustomBaseSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LLMSettings(CustomBaseSettings):
    # api_base: str = Field(env="OPENAI_API_BASE", default="https://api.gptapi.cyou/v1")
    # api_key: str = Field(env="OPENAI_API_KEY", default="sk-MrymAdMULNCmANziD6Bb5e51925047EdBf416377294bE673")
    # default_model: str = Field(env="DEFAULT_MODEL", default="gpt-3.5-turbo")

    api_base: str = Field(env="OPENAI_API_BASE", default="https://api.nextapi.fun/v1")
    api_key: str = Field(env="OPENAI_API_KEY", default="ak-rijxawD5sZxxnXXEoJmpWG52QlAMYxxaEQmp1ixrcJQOtbVY")
    default_model: str = Field(env="DEFAULT_MODEL", default="gpt-3.5-turbo-0125")
    # default_model: str = Field(env="DEFAULT_MODEL", default="gpt-4-0125-preview")


class DatabaseSettings(CustomBaseSettings):
    url: str = Field(env="DATABASE_URL", default="mongodb+srv://aflybird0:8ORG2lDRRm36ntP7@cluster0.lh2vpp8.mongodb.net/?retryWrites=true&w=majority")
    db_name: str = Field(env="DATABASE_NAME", default="cluster0")

class DockerSettings(CustomBaseSettings):
    docker_port: str = Field(env="DOCKER_PORT", default="8080")
    docker_host: str = Field(env="DOCKER_HOST", default="localhost")


class Settings(BaseSettings):
    llm: LLMSettings = Field(default_factory=LLMSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    docker: DockerSettings = Field(default_factory=DockerSettings)


@lru_cache
def get_settings():
    settings = Settings()
    return settings


if __name__ == '__main__':
    print(get_settings().json(indent=2))