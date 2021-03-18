# -*- coding: utf-8 -*-


from sys import argv

from iapc.tools import Plugin, action, parseQuery, openSettings, getSetting

from dlive import home, styles, search_queries
from dlive.client import client
from dlive.objects import Folders
from dlive.persistence import search_cache, search_history
from dlive.utils import settingsItem, moreItem, newSearchItem


# ------------------------------------------------------------------------------
# DLivePlugin

class DLivePlugin(Plugin):

    # helpers ------------------------------------------------------------------

    def getSubfolders(self, type, **kwargs):
        return Folders(
            {"type": type, "style": style, "kwargs": kwargs}
            for style in styles[type]
        )

    def addNewSearch(self, **kwargs):
        return self.addItem(
            newSearchItem(self.url, action="search", new=True, **kwargs)
        )

    def addSettings(self):
        if getSetting("settings", bool):
            return self.addItem(settingsItem(self.url, action="settings"))
        return True

    def addDirectory(self, items, *args, **kwargs):
        if super().addDirectory(items, *args):
            if items.hasNextPage:
                kwargs["after"] = items.endCursor
                return self.addItem(
                    moreItem(self.url, action=self.action, **kwargs)
                )
            return True
        return False

    # stream -------------------------------------------------------------------

    @action()
    def stream(self, **kwargs):
        if (item := client.stream(**kwargs)):
            return self.playItem(item)
        return False

    # user ---------------------------------------------------------------------

    @action()
    def user(self, **kwargs):
        stream, vods = client.user(**kwargs)
        if stream:
            self.addItem(stream.getItem(self.url, "stream"))
        return self.addDirectory(vods, **kwargs)

    # category -----------------------------------------------------------------

    @action()
    def category(self, **kwargs):
        return self.addDirectory(client.category(**kwargs), "stream", **kwargs)

    # home ---------------------------------------------------------------------

    @action()
    def home(self, **kwargs):
        if self.addDirectory(Folders(home)):
            return self.addSettings()
        return False

    # featured -----------------------------------------------------------------

    @action(category=30007)
    def featured(self, **kwargs):
        return self.addDirectory(client.featured(**kwargs), "stream")

    # recommended --------------------------------------------------------------

    @action(category=30009)
    def recommended(self, **kwargs):
        return self.addDirectory(client.recommended(**kwargs), "user")

    # streams ------------------------------------------------------------------

    @action(category=30004)
    def streams(self, **kwargs):
        return self.addDirectory(client.streams(**kwargs), "stream", **kwargs)

    # categories ---------------------------------------------------------------

    @action(category=30006)
    def categories(self, **kwargs):
        return self.addDirectory(
            client.categories(**kwargs), "category", **kwargs
        )

    # search -------------------------------------------------------------------

    def __search__(self, **kwargs):
        search_cache.push(kwargs)
        return self.addDirectory(
            client.search(**kwargs),
            search_queries[kwargs["query"]]["action"], **kwargs
        )

    def __new_search__(self, **kwargs):
        try:
            kwargs = search_cache.pop()
        except IndexError:
            kwargs = search_history.new(**kwargs)
        if "text" in kwargs:
            return self.__search__(**kwargs)
        return False

    def __history__(self, **kwargs):
        search_cache.clear()
        if self.addNewSearch(**kwargs):
            return self.addDirectory(
                search_history.history(
                    category=search_queries[kwargs["query"]]["category"],
                    **kwargs
                )
            )
        return False

    @action(category=30002)
    def search(self, **kwargs):
        if "query" in kwargs:
            new = kwargs.pop("new", False)
            if "text" in kwargs:
                return self.__search__(**kwargs)
            if new:
                return self.__new_search__(**kwargs)
            return self.__history__(**kwargs)
        search_cache.clear()
        return self.addDirectory(self.getSubfolders("search"))

    # settings -----------------------------------------------------------------

    @action(directory=False)
    def settings(self, **kwargs):
        openSettings()
        return True


# __main__ ---------------------------------------------------------------------

def dispatch(url, handle, query, *args):
    DLivePlugin(url, int(handle)).dispatch(**parseQuery(query))


if __name__ == "__main__":
    dispatch(*argv)

