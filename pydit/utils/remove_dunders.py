from pydit.utils.is_dunder import is_dunder


def remove_dunders(items: list[str]) -> list[str]:
    return [item for item in items if not is_dunder(item)]
