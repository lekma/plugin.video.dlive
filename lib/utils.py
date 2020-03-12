# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


from os.path import join

from six import text_type, iteritems
from six.moves.urllib.parse import parse_qsl, urlencode
from kodi_six import xbmc, xbmcaddon, xbmcgui

from . import _subfolders_defaults_


addon = xbmcaddon.Addon()
addon_path = xbmc.translatePath(addon.getAddonInfo("path"))

dialog = xbmcgui.Dialog()


def parse_query(query):
    if query.startswith("?"):
        query = query[1:]
    return dict(parse_qsl(query))


def build_url(*args, **kwargs):
    params = {k: v.encode("utf-8") if isinstance(v, text_type) else v
              for k, v in iteritems(kwargs)}
    return "?".join(("/".join(args), urlencode(params)))


def localized_string(id):
    if id < 30000:
        return xbmc.getLocalizedString(id)
    return addon.getLocalizedString(id)


def get_media_path(*args):
    return join(addon_path, "resources", "media", *args)

def get_icon(name):
    return get_media_path("{}.png".format(name))


def get_subfolders(style, subfolders=_subfolders_defaults_):
    return [{"type": folder, "style": style} for folder in subfolders]


# settings ---------------------------------------------------------------------

_get_settings_ = {
    bool: "getSettingBool",
    int: "getSettingInt",
    float: "getSettingNumber",
    unicode: "getSettingString"
}

def get_setting(id, _type=None):
    if _type is not None:
        return _type(getattr(addon, _get_settings_.get(_type, "getSetting"))(id))
    return addon.getSetting(id)


# logging ----------------------------------------------------------------------

def log(msg, level=xbmc.LOGNOTICE):
    xbmc.log("{}: {}".format(addon.getAddonInfo("id"), msg), level=level)


def debug(msg):
    log(msg, xbmc.LOGDEBUG)


def warn(msg):
    log(msg, xbmc.LOGWARNING)


# listitem ---------------------------------------------------------------------

class ListItem(xbmcgui.ListItem):

    def __new__(cls, label, path, **kwargs):
        return super(ListItem, cls).__new__(
            cls, label=label, path=path, iconImage="", thumbnailImage="",
            offscreen=True)

    def __init__(self, label, path, isFolder=False, infos=None,
                 streamInfos=None, **art):
        self.setIsFolder(isFolder)
        self.setIsPlayable(not isFolder)
        self.isFolder = isFolder
        if infos:
            for info in iteritems(infos):
                self.setInfo(*info)
        if streamInfos:
            for info in iteritems(streamInfos):
                self.addStreamInfo(*info)
        if art:
            self.setArt(art)

    def setIsPlayable(self, isPlayable):
        self.setProperty("IsPlayable", "true" if isPlayable else "false")

    def asItem(self):
        return self.getPath(), self, self.isFolder


_more_label_ = localized_string(30099)
_more_icon_ = get_icon("more")

def more_item(url, **kwargs):
    return ListItem(
        _more_label_,  build_url(url, **kwargs), isFolder=True,
        infos={"video": {"plot": _more_label_}}, icon=_more_icon_)


# quality ----------------------------------------------------------------------

class Quality(object):

    # This has to reflect the 'stream_quality'/'vod_quality' settings.
    # At the time of this writing, the order was:
    # ["Auto", "1080p", "720p", "480p", "360p", "Always Ask", "Adaptive"]
    _settings_ = (0, 1080, 720, 480, 360)

    def __init__(self, playlist):
        self.uri = playlist.uri
        self.bandwidth = playlist.stream_info.bandwidth
        self.width, self.height = playlist.stream_info.resolution

    def __str__(self):
        return "{0.width}x{0.height}@{0.bandwidth}bps".format(self)

    @classmethod
    def select(cls, qualities):
        return dialog.select(
            cls._heading_, [str(quality) for quality in qualities])

    @classmethod
    def best_match(cls, quality, qualities):
        height = cls._settings_[quality]
        # we know/assume/hope the list is already sorted by height in descending order
        for i, q in enumerate(qualities):
            if q.height <= height: # exact match or closest below
                return i
        # what to do when the above fails to find a match?
        # we could pop a dialog asking for manual selection, something like:
        # return cls.select(qualities)
        # for the time being, we just fail.
        return -1


class StreamQuality(Quality):

    _heading_ = localized_string(30121)


class VodQuality(Quality):

    _heading_ = localized_string(30122)


# search -----------------------------------------------------------------------

_search_label_ = localized_string(30002)

def search_dialog():
    return dialog.input(_search_label_)


# notify -----------------------------------------------------------------------

_notify_heading_ = localized_string(30000)

def notify(message, heading=_notify_heading_, icon=xbmcgui.NOTIFICATION_ERROR,
           time=2000):
    if isinstance(message, int):
        message = localized_string(message)
    dialog.notification(heading, message, icon, time)

