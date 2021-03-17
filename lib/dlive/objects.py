# -*- coding: utf-8 -*-


from datetime import datetime

from tools import localizedString, maybeLocalize, getAddonId, ListItem, buildUrl
from tools.objects import Type, Object, List

from . import __schema__


# ------------------------------------------------------------------------------
# Item

def __date__(value):
    if isinstance(value, str):
        return datetime.fromtimestamp(int(value) / 1000)
    return value


class ItemType(Type):

    __transform__ = {"__date__": __date__}


class Item(Object, metaclass=ItemType):

    __menus__ = []

    @classmethod
    def menus(cls, **kwargs):
        return [
            (
                maybeLocalize(label).format(**kwargs),
                action.format(addonId=getAddonId(), **kwargs)
            )
            for label, action in cls.__menus__
        ]

    @property
    def plot(self):
        return self.__plot__.format(self)


# ------------------------------------------------------------------------------
# Items

class Items(List):

    __ctor__ = Item

    def __init__(self, items, endCursor="-1", hasNextPage=False, **kwargs):
        super().__init__(items, **kwargs)
        self.endCursor = endCursor
        self.hasNextPage = hasNextPage


# ------------------------------------------------------------------------------
# Folders

class Folder(Item):

    @property
    def style(self):
        return self.get("style", "")

    @property
    def kwargs(self):
        return self.get("kwargs", {})

    def getItem(self, url, **kwargs):
        folder = __schema__[self.type][self.style]
        label = maybeLocalize(folder["label"])
        kwargs = dict(dict(folder.get("kwargs", {}), **self.kwargs), **kwargs)
        return ListItem(
            label,
            buildUrl(url, action=folder.get("action", self.type), **kwargs),
            isFolder=True,
            infos={
                "video": {
                    "title": label,
                    "plot": maybeLocalize(folder.get("plot", label))
                }
            },
            **folder.get("art", {})
        )


class Folders(Items):

    __ctor__ = Folder


# ------------------------------------------------------------------------------
# Categories

class Category(Item):

    __plot__ = localizedString(30053)

    @property
    def thumbnail(self):
        return self.imgUrl or "DefaultGenre.png"

    def getItem(self, url, action):
        return ListItem(
            self.title,
            buildUrl(url, action=action, categoryID=self.backendID),
            isFolder=True,
            infos={"video": {"title": self.title, "plot": self.plot}},
            poster=self.thumbnail,
            thumb=self.thumbnail
        )


class Categories(Items):

    __ctor__ = Category


# ------------------------------------------------------------------------------
# Users

class User(Item):

    __plot__ = localizedString(30054)

    @property
    def livestream(self):
        return Livestream(self["livestream"])

    @property
    def pastBroadcasts(self):
        vods = self.get("pastBroadcasts", {})
        return PastBroadcasts(
            vods.get("list", []),
            category=self.displayname,
            **vods.get("pageInfo", {})
        )

    @property
    def followers(self):
        return self.get("followers", {}).get("totalCount", 0)

    @property
    def thumbnail(self):
        return self.avatar or "DefaultArtist.png"

    def getItem(self, url, action):
        return ListItem(
            self.displayname,
            buildUrl(url, action=action, username=self.username),
            isFolder=True,
            infos={"video": {"title": self.displayname, "plot": self.plot}},
            poster=self.thumbnail,
            thumb=self.thumbnail
        )


class Users(Items):

    __ctor__ = User


# ------------------------------------------------------------------------------
# Video

class Video(Item):

    __transform__ = {"language": Object, "category": Category, "creator": User}
    __date__ = {"createdAt"}
    __infos__ = {"mediatype": "video"}

    @property
    def rating(self):
        return localizedString(30052) if self.ageRestriction else ""

    @property
    def infos(self):
        return self.__infos__

    @property
    def thumbnail(self):
        return self.thumbnailUrl or "DefaultAddonVideo.png"

    def makeItem(self, path):
        return ListItem(
            self.title,
            path,
            infos={"video": dict(self.infos, title=self.title, plot=self.plot)},
            thumb=self.thumbnail
        )


# ------------------------------------------------------------------------------
# Livestream

class Livestream(Video):

    __plot__ = localizedString(30055)

    @property
    def infos(self):
        return dict(self.__infos__, playcount=0)

    #def makeItem(self, path):
    #    item = super().makeItem(path)
    #    item.setLabel(f"[COLOR red][LIVE][/COLOR] {self.title}")
    #    return item

    def getItem(self, url, action):
        return self.makeItem(
            buildUrl(url, action=action, username=self.creator.username)
        )


# ------------------------------------------------------------------------------
# Streams

class Stream(Livestream):

    __menus__ = [
        (30031, "RunScript({addonId},goToUser,{username})")
    ]

    def makeItem(self, path):
        item = super().makeItem(path)
        item.setLabel(f"{self.creator.displayname} - {self.title}")
        item.addContextMenuItems(self.menus(username=self.creator.username))
        return item


class Streams(Items):

    __ctor__ = Stream


# ------------------------------------------------------------------------------
# PastBroadcasts

class PastBroadcast(Video):

    __plot__ = localizedString(30056)

    def makeItem(self, path):
        item = super().makeItem(path)
        item.addStreamInfo("video", {"duration": self.length})
        return item

    def getItem(self, *args):
        return self.makeItem(self.playbackUrl)


class PastBroadcasts(Items):

    __ctor__ = PastBroadcast


# ------------------------------------------------------------------------------
# Queries

class Query(Item):

    __menus__ = [
        (30035, "RunScript({addonId},removeSearchQuery,{query},{text})"),
        (30036, "RunScript({addonId},clearSearchHistory,{query})")
    ]

    def getItem(self, url):
        return ListItem(
            self.text,
            buildUrl(url, action="search", query=self.query, text=self.text),
            isFolder=True,
            infos={"video": {"title": self.text, "plot": self.text}},
            contextMenus=self.menus(query=self.query, text=self.text),
            poster="DefaultAddonsSearch.png",
            thumb="DefaultAddonsSearch.png"
        )


class Queries(Items):

    __ctor__ = Query

