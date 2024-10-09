from typing import Any, cast, overload


DictItemType = dict[str, Any]
ListItemType = list[str]
KlassType = type[Any]


@overload
def remove_private_and_protected_items(
    items: DictItemType, klass: KlassType
) -> DictItemType:
    pass


@overload
def remove_private_and_protected_items(
    items: ListItemType, klass: KlassType
) -> ListItemType:
    pass


def remove_private_and_protected_items(
    items: ListItemType | DictItemType, klass: KlassType
) -> ListItemType | DictItemType:

    if type(items) is list:
        return _remove_private_and_protected_items_list(items, klass)

    return _remove_private_and_protected_items_dict(cast(DictItemType, items), klass)


def _remove_private_and_protected_items_list(
    items: ListItemType, klass: KlassType
) -> ListItemType:
    response: ListItemType = []

    for item in items:
        if _is_private_or_protected(item, klass):
            continue

        response.append(item)

    return response


def _remove_private_and_protected_items_dict(
    items: DictItemType, klass: KlassType
) -> DictItemType:
    response: DictItemType = {}

    for item in items.keys():
        if _is_private_or_protected(item, klass):
            continue

        response[item] = items[item]

    return response


def _is_private_or_protected(key: str, klass: KlassType) -> bool:
    return key.find(f"_{klass.__name__}__") != -1 or key.startswith("_")
