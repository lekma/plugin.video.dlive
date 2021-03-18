# -*- coding: utf-8 -*-


from collections import deque, OrderedDict

from iapc.tools import Persistent, save, notify

from .objects import Queries
from .utils import searchDialog


# ------------------------------------------------------------------------------
# SearchCache

class SearchCache(Persistent, deque):

    @save
    def clear(self):
        super().clear()

    @save
    def push(self, item):
        super().append(item)

    @save
    def pop(self):
        return super().pop()


search_cache = SearchCache()


# ------------------------------------------------------------------------------
# SearchHistory

class SearchHistory(Persistent, dict):

    def __missing__(self, key):
        self[key] = OrderedDict()
        return self[key]

    @save
    def new(self, **kwargs):
        if (text := searchDialog()):
            kwargs["text"] = text
            self[kwargs["query"]][text] = kwargs
        return kwargs

    @save
    def remove(self, **kwargs):
        del self[kwargs["query"]][kwargs["text"]]

    @save
    def clear(self, **kwargs):
        if (query := kwargs.get("query")):
            self[query].clear()
        else:
            super().clear()
            notify(30114, time=2000)

    def history(self, category=None, **kwargs):
        return Queries(
            reversed(self[kwargs["query"]].values()), category=category
        )


search_history = SearchHistory()

