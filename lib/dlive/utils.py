# -*- coding: utf-8 -*-


from tools import (
    localizedString, ListItem, buildUrl, getMedia, executeBuiltin, inputDialog
)


# misc useful items ------------------------------------------------------------

def __makeItem__(label, url, art=None, isFolder=True, **kwargs):
    label = localizedString(label)
    return ListItem(
        label,
        buildUrl(url, **kwargs),
        isFolder=isFolder,
        isPlayable=False,
        infos={"video": {"title": label, "plot": label}},
        icon=art,
        poster=art,
        thumb=art
    )


# settings item
def settingsItem(url, **kwargs):
    return __makeItem__(
        30100, url, "icons/settings/system.png", isFolder=False, **kwargs
    )


# more item
__more_art__ = getMedia("more")

def moreItem(url, **kwargs):
    return __makeItem__(30099, url, __more_art__, **kwargs)


# newSearch item
def newSearchItem(url, **kwargs):
    return __makeItem__(30098, url, "DefaultAddSource.png", **kwargs)


# search -----------------------------------------------------------------------

def searchDialog():
    return inputDialog(heading=30002)


# ------------------------------------------------------------------------------
# Cache

class Cache(dict):

    __getters__ = {
        dict: dict.__getitem__,
        object: getattr
    }

    def __init_subclass__(cls, key, key_type=str, item_type=dict, **kwargs):
        cls.__key__ = key
        cls.__type__ = key_type
        cls.__getter__ = cls.__getters__[item_type]
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_key(cls, item):
        return cls.__type__(cls.__getter__(item, cls.__key__))

    # --------------------------------------------------------------------------

    missing = None

    def __missing__(self, key):
        if self.missing is not None:
            return self.missing
        raise KeyError(key)

    def __init__(self, items=None):
        super().__init__((self.get_key(item), item) for item in (items or []))

    def update(self, items):
        return super().update((self.get_key(item), item) for item in items)

