# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


from datetime import datetime

from six import string_types, iteritems, with_metaclass, raise_from

from utils import ListItem, buildUrl, localizedString


# ------------------------------------------------------------------------------
# base types
# ------------------------------------------------------------------------------

def _date_(value):
    if isinstance(value, string_types):
        return datetime.fromtimestamp(int(value) / 1000)
    return value

def _json_(name, func):
    def getter(obj):
        return func(obj.__getattr__(name))
    return property(getter)


class DLiveType(type):

    __json__ = {"__date__": _date_}
    __attr_error__ = "'{}' object has no attribute '{{}}'"

    def __new__(cls, name, bases, namespace, **kwargs):
        namespace.setdefault("__slots__", set())
        namespace.setdefault("__attr_error__", cls.__attr_error__.format(name))
        for _name, _func in iteritems(namespace.pop("__json__", dict())):
            namespace[_name] = _json_(_name, _func)
        for _type, _func in iteritems(cls.__json__):
            for _name in namespace.pop(_type, set()):
                namespace[_name] = _json_(_name, _func)
        return type.__new__(cls, name, bases, namespace, **kwargs)


class DLiveObject(with_metaclass(DLiveType, object)):

    __slots__ = {"__data__"}

    def __new__(cls, data):
        if isinstance(data, dict):
            if not data:
                return None
            return super(DLiveObject, cls).__new__(cls)
        return data

    def __init__(self, data):
        self.__data__ = data

    def __getitem__(self, name):
        return self.__data__[name]

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise_from(AttributeError(self.__attr_error__.format(name)), None)

    def __repr__(self):
        try:
            _repr_ = self._repr_
        except AttributeError:
            return super(DLiveObject, self).__repr__()
        else:
            return _repr_.format(self)


# folders ----------------------------------------------------------------------

_folders_schema_ = {
    "streams": {
        "": {
            "id": 30004
        },
        "featured": {
            "id": 30007,
            "action": "featured"
        }
    },
    "categories": {
        "": {
            "id": 30006
        }
    },
    "users": {
        "recommended": {
            "id": 30009,
            "action": "recommended"
        }
    },
    "search": {
        "": {
            "id": 30002
        },
        "users": {
            "id": 30003,
            "action": "search_users"
        },
        "categories": {
            "id": 30006,
            "action": "search_categories"
        }
    }
}


_home_folders_ = (
    {"type": "streams", "style": "featured"},
    {"type": "users", "style": "recommended"},
    {"type": "streams"},
    {"type": "categories"},
    {"type": "search"}
)


_search_styles_ = ("users", "categories")


class Folder(DLiveObject):

    @property
    def style(self):
        try:
            return self["style"] or ""
        except KeyError:
            return ""

    def item(self, url, **kwargs):
        folder = _folders_schema_[self.type][self.style]
        label = folder["id"]
        if isinstance(label, int):
            label = localizedString(label)
        action = folder.get("action", self.type)
        kwargs.update(folder.get("kwargs", {}))
        plot = folder.get("plot", label)
        if isinstance(plot, int):
            plot = localizedString(plot)
        return ListItem(
            label, buildUrl(url, action=action, **kwargs), isFolder=True,
            infos={"video": {"title": label, "plot": plot}})


# ------------------------------------------------------------------------------
# DLive objects
# ------------------------------------------------------------------------------

# https://dev.dlive.tv/schema/node.doc.html
class Node(DLiveObject):

    _repr_ = "Node({0.id})"


# https://dev.dlive.tv/schema/language.doc.html
class Language(Node):

    _repr_ = "Language({0.backendID}, language={0.language})"


class DLiveItem(Node):

    _menus_ = []

    def plot(self):
        return self._plot_.format(self)

    def menus(self, **kwargs):
        return [(localizedString(label),
                 action.format(addonId=getAddonId(), **kwargs))
                for label, action in self._menus_]


# categories -------------------------------------------------------------------

# https://dev.dlive.tv/schema/category.doc.html
class Category(DLiveItem):

    _repr_ = "Category({0.backendID}, title={0.title})"
    _plot_ = localizedString(30053)

    def item(self, url, action):
        if self.backendID:
            return ListItem(
                self.title,
                buildUrl(url, action=action, categoryID=self.backendID),
                isFolder=True,
                infos={"video": {"plot": self.plot()}},
                poster=self.imgUrl)


# users ------------------------------------------------------------------------

# https://dev.dlive.tv/schema/user.doc.html
class User(DLiveItem):

    __date__ = {"createdAt"}
    _repr_ = "User({0.username}, displayname={0.displayname})"
    _plot_ = localizedString(30054)

    @property
    def livestream(self):
        return Livestream(self["livestream"])

    @property
    def pastBroadcasts(self):
        try:
            vods = self["pastBroadcasts"]
        except KeyError:
            vods = {}
        return PastBroadcasts(vods.get("list", []), category=self.displayname,
                              **vods.get("pageInfo", {}))

    @property
    def followers(self):
        try:
            return self["followers"]["totalCount"]
        except KeyError:
            return 0

    def item(self, url, action):
        return ListItem(
            self.displayname,
            buildUrl(url, action=action, username=self.username),
            isFolder=True,
            infos={"video": {"plot": self.plot()}},
            poster=self.avatar)


# streams ----------------------------------------------------------------------

# https://dev.dlive.tv/schema/livestream.doc.html
class Livestream(DLiveItem):

    __json__ = {"language": Language, "category": Category, "creator": User}
    __date__ = {"createdAt"}
    _repr_ = "Livestream({0.permlink})"
    _plot_ = localizedString(30055)
    _video_infos_ = {"mediatype": "video", "playcount": 0}

    @property
    def rating(self):
        return localizedString(30052) if self.ageRestriction else ""

    def _item(self, path):
        title = " - ".join((self.creator.displayname, self.title))
        return ListItem(
            title,
            path,
            infos={"video": dict(self._video_infos_,
                                 title=title, plot=self.plot())},
            thumb=self.thumbnailUrl)

    def item(self, url, action):
        return self._item(
            buildUrl(url, action=action, username=self.creator.username))


# vods -------------------------------------------------------------------------

# https://dev.dlive.tv/schema/resolution.doc.html
class Resolution(DLiveObject):

    _repr_ = "Resolution({0.url}, resolution={0.resolution})"


# https://dev.dlive.tv/schema/pastbroadcast.doc.html
class PastBroadcast(DLiveItem):

    __json__ = {"language": Language, "category": Category, "creator": User}
    __date__ = {"createdAt"}
    _repr_ = "PastBroadcast({0.permlink})"
    _plot_ = localizedString(30056)
    _video_infos_ = {"mediatype": "video"}

    @property
    def rating(self):
        return localizedString(30052) if self.ageRestriction else ""

    def _item(self, path):
        streamInfos = {"video": {"duration": self.length}}
        item = ListItem(
            self.title,
            path,
            infos={"video": dict(self._video_infos_,
                                 title=self.title, plot=self.plot())},
            streamInfos=streamInfos,
            thumb=self.thumbnailUrl)
        return item

    def item(self, *args):
        return self._item(self.playbackUrl)



# ------------------------------------------------------------------------------
# lists, collections
# ------------------------------------------------------------------------------

class DLiveItems(list):

    _ctor_ = DLiveObject
    _content_ = "videos"
    _category_ = None

    def __init__(self, items, endCursor="-1", hasNextPage=False,
                 content=None, category=None):
        super(DLiveItems, self).__init__((self._ctor_(item) for item in items))
        self.endCursor = endCursor
        self.hasNextPage = hasNextPage
        self.content = content or self._content_
        self.category = category or self._category_

    def items(self, *args):
        return (item.item(*args) for item in self if item)


class Folders(DLiveItems):

    _ctor_ = Folder


class Home(Folders):

    def __init__(self):
        super(Home, self).__init__(_home_folders_)


class Users(DLiveItems):

    _ctor_ = User


class Categories(DLiveItems):

    _ctor_ = Category


class Livestreams(DLiveItems):

    _ctor_ = Livestream


class PastBroadcasts(DLiveItems):

    _ctor_ = PastBroadcast

