from typing import Self

from . import element


class Sequence(element.Element):
    def __init__(self, *children):
        super().__init__()
        self.children = list(children)

    def _add(self, element: Self):
        self.children.append(element)


class Bag(element.Element):
    def __init__(self, *children):
        super().__init__()
        self.children = set(children)

    def _add(self, element: Self):
        self.children.add(element)
