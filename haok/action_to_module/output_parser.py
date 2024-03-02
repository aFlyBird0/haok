import json
import re

from langchain.agents import AgentOutputParser
from langchain_core.agents import AgentFinish
from langchain_core.exceptions import OutputParserException
from pydantic.json import pydantic_encoder

from haok.module.module import Module, Param

# 写一个函数，把输出中的json和python代码提取出来
example_dict = {
    "name": "is_prime",
    "description": "Check if a number is prime.",
    "tags": ["math", "prime"],
    "params": [
        Param(name="number", param_type="int", description="The number to check")
    ],
}

example_json = json.dumps(example_dict, indent=4,  default=pydantic_encoder)
example_python_code = """
def is_prime(number):
    if number <= 1:
        return False
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            return False
    return True

# number_to_check = 100

if is_prime(number_to_check):
    print(f"{number_to_check} is prime")
else:
    print(f"{number_to_check} is not prime")
"""

example = f"""
```json
{example_json}
```
```python
{example_python_code}
```
"""

def split_json_and_code(text) -> (str, str):
    json_pattern = r'```json(.*?)```'
    python_pattern = r'```python(.*?)```'

    json_match = re.search(json_pattern, text, re.DOTALL)
    python_match = re.search(python_pattern, text, re.DOTALL)

    json_block = json.loads(json_match.group(1).strip()) if json_match else None
    python_block = python_match.group(1).strip() if python_match else None

    return json_block, python_block


class ArgsAndCodeOutputParser(AgentOutputParser):
    def parse(self, output) -> AgentFinish:
        """
        :param output: LLM的输出
        :return: json, python_code
        """
        json_data, python_code = split_json_and_code(output)
        if json_data and python_code:
            # module = Module(
            #     name=json_data["name"],
            #     description=json_data["description"],
            #     tags=json_data["tags"],
            #     code=python_code,
            #     # args=json_data["args"],
            #     params=json_data["params"],
            #     dependencies=json_data["dependencies"]
            # )
            json_data["code"] = python_code
            module = Module.from_json(json_data)
            return AgentFinish(
                return_values={
                    "module": module,
                },
                log=output,
            )
        else:
            raise OutputParserException(
                f"Could not parse LLM output: `{output}`",
                observation="You should only provide one json block and one python code block as the example above.",
                llm_output=output,
                send_to_llm=True,
            )


if __name__ == "__main__":
    dict_gotten, code_gotten = split_json_and_code(example)
    print(dict_gotten, "\n", code_gotten)
    assert dict_gotten == example_dict

    parser = ArgsAndCodeOutputParser()
    finish = parser.parse(example)
    print(finish.return_values["module"].to_dict())
