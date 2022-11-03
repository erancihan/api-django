from typing import Any


class ChangesMixin:
    def __setattr__(self, name: str, value: Any) -> None:
        setter_func = getattr(self, f"setter_{name}", None)
        if setter_func:
            setter_func(value)

        if name in self.__dict__ and getattr(self, name) != value:
            super().__setattr__(f"{name}__changed", True)
        super().__setattr__(name, value)
