from typing import Callable


class Validator:
    def __init__(self, name: str, predicate: Callable[[], bool]):
        self.name = name
        self.predicate = predicate

    def validate(self) -> bool:
        return self.predicate()
