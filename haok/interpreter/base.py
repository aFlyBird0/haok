class BaseInterpreter:
    name: str = "base_interpreter"
    description: str = "A base interpreter"

    def run(self, code: str, **kwargs):
        raise NotImplementedError()

    def setup(self, code: str):
        raise NotImplementedError()