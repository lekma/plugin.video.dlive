# -*- coding: utf-8 -*-


from sys import argv

from tools import Plugin, action, parseQuery, openSettings, getSetting

from dlive import home, styles
from dlive.client import client
from dlive.objects import Folders
from dlive.utils import moreItem, settingsItem, searchDialog


# ------------------------------------------------------------------------------
# DLivePlugin

class DLivePlugin(Plugin):

    # helpers ------------------------------------------------------------------

    def getSubfolders(self, type, **kwargs):
        return Folders(
            {"type": type, "style": style, "kwargs": kwargs}
            for style in styles[type]
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

    @action(category=30002)
    def search(self, **kwargs):
        return self.addDirectory(self.getSubfolders("search"))

    @action(category=30003)
    def search_users(self, **kwargs):
        if (text := kwargs.pop("text", "") or searchDialog()):
            return self.addDirectory(
                client.search_users(text=text, **kwargs),
                "user", text=text, **kwargs
            )
        return False

    @action(category=30006)
    def search_categories(self, **kwargs):
        if (text := kwargs.pop("text", "") or searchDialog()):
            return self.addDirectory(
                client.search_categories(text=text, **kwargs),
                "category", text=text, **kwargs
            )
        return False

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

