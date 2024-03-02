import json

from pydantic.json import pydantic_encoder

from haok.module.module import Param

example_origin_code = """
def fibonacci(n):
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b

    return b
number = 10
print(fibonacci(number))
"""

example_refactored_code = """
def fibonacci(n):
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b

    return b
# 所有对形参的赋值语句都应该被忽略，假设所有实参已经被正确赋值。
# number = 10
print(fibonacci(number))
"""

example_args_extracted_json = {
    "name": "fibonacci",
    "description": "Calculate the fibonacci number of n.",
    "args": {
        "number": "int"
    },
    "params": [
        Param(name="number", param_type="int", description="第一个参数", required=True)
    ],
    "tags": ["math", "fibonacci", "calculation"],
    "dependencies": []
}

example_cn_additional_info = """
值得注意的是：
1. 虽然函数的形参是n，但是实际调用函数时，传入的实参是number。你应该以实际传入的实参名称为准，即在Json中，参数名称应该是number。其他情况也是如此。
2. 上面的代码重构中，"number=10"是对实参的初始化/赋值语句，你应该直接删掉这一行，假设n已经被正确赋值。你应该假设所有调用函数时，实参都已经被正确赋值。
"""

example_cn = {
    "example_origin_code": example_origin_code,
    "example_task_log": "I want to calculate the fibonacci number of 10.",
    "example_origin_main_task": "What is the fibonacci number of 10 plus 23 and minus the 5th prime number?",
    "example_refactored_code": example_refactored_code,
    "example_args_extracted_json": json.dumps(example_args_extracted_json, indent=4, default=pydantic_encoder),
    "example_additional_info": example_cn_additional_info,
}
