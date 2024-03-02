from typing import List

from langchain.utilities.python import PythonREPL

from .base import BaseInterpreter
from .shell import ShellExecutor, ShellInterpreter


class PythonInterpreter(BaseInterpreter):
    name = "python"
    description = "Executes python code on the user's machine and returns the output"

    def __init__(self):
        self.namespace = {}

    def run(self, code: str, **kwargs):
        # merge namespace with kwargs
        self.namespace.update(kwargs)
        return PythonREPL(_globals=self.namespace, _locals=None).run(code)

    def setup(self, code: str):
        self.run(code)

    def install_dependencies(self, dependencies: List[str])->dict:
        # print(dependencies)
        if not dependencies or len(dependencies) == 0:
            return {"status": "success", "stdout": "", "stderr": ""}
        commands = []
        for dep in dependencies:
            commands.append(f"pip install {dep}")
        # return ShellInterpreter().run("\n".join(commands))
        return ShellExecutor.run("\n".join(commands), timeout=120)