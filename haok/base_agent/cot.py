from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from haok.llm.openai import OpenAIConfig

def CoT(question: str, task_prefix, example):
    # task_prefix += "Let's think step by step"
    examples = [example]
    # 对 dyck_languages 做特殊判断
    if task_prefix.startswith("You will receive a sequence,"):
        example_prompt = PromptTemplate(
            input_variables=["question", "answer"], template="Question: " + task_prefix + "{question}\nAnswer: {answer}"
        )
    else:
        example_prompt = PromptTemplate(
            input_variables=["question", "answer"], template="Question: " + task_prefix + "{question}\n{answer}"
        )
    # example_prompt = PromptTemplate(
    #     input_variables=["question", "answer"], template="Question: " + task_prefix + "{question}\n{answer}"
    # )
    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        suffix="Question: " + task_prefix + "{input}",
        input_variables=["input"],
    )
    output_parser = StrOutputParser()
    llm = OpenAIConfig.defaultLLM()
    chain = (
            {"input": RunnablePassthrough()}
            | prompt
            | llm
            | output_parser
    )

    return chain.invoke(question)