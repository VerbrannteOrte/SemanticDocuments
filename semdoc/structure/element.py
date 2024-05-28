from collections import defaultdict
from dataclasses import dataclass
from typing import Self

from . import region


class Element:
    def __init__(self):
        self.children = iter(())
        self.properties = defaultdict(list)

    def iter_regions(self):
        for element in self.children:
            yield element

    def set_property(self, key: str, value, source: str, confidence: float = 1.0):
        prop = Property(key, value, source, confidence)
        self.properties[key].append(prop)

    def get_property(self, key: str):
        data = self.properties[key]
        max_conf = 0
        strongest = None
        for prop in data:
            if prop.confidence > max_conf:
                strongest = prop
        if strongest:
            return strongest.value
        else:
            raise KeyError()

    def set_text(self, text: str, source: str, confidence: float = 1.0):
        prop = Property("text", text, source, confidence)
        self.properties["text"].append(prop)

    def add(self, element: Self):
        self._add(element)

    def _add(self, element: Self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def get_text(self):
        try:
            return self.get_property("text")
        except KeyError:
            return ""

    def is_region(self):
        return type(self) is region.Region

    def children_ordered(self):
        yield from sorted(self.children, key=lambda c: c.y and c.y)

    def to_dict(self):
        children = [child.to_dict() for child in self.children]
        properties = {key: self.get_property(key) for key in self.properties.keys()}
        return {
            "children": children,
            "properties": properties,
        }


@dataclass
class Property:
    def __init__(self, key: str, value, source: str, confidence: float):
        if not 0 <= confidence <= 1:
            raise ValueError(f"Invalid confidence: {confidence}")
        self.key = key
        self.value = value
        self.confidence = confidence
        self.source = source

    def __repr__(self):
        return f"Property({self.key!r}, {self.value!r}, {self.source!r}, {self.confidence!r})"

    def __str__(self):
        return f"{self.key}: {self.value} ({self.source}: {self.confidence})"
