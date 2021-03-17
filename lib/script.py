# -*- coding: utf-8 -*-


from sys import argv

from tools import getAddonId, containerUpdate, containerRefresh

from dlive.persistence import search_history


__plugin_url__ = f"plugin://{getAddonId()}"


# user -------------------------------------------------------------------------

__user_url__ = f"{__plugin_url__}/?action=user&username={{}}"

def goToUser(username):
    containerUpdate(__user_url__.format(username))


# search -----------------------------------------------------------------------

def removeSearchQuery(query, text):
    search_history.remove(query=query, text=text)
    containerRefresh()

def clearSearchHistory(query=None):
    search_history.clear(query=query)
    containerRefresh()


# __main__ ---------------------------------------------------------------------

__dispatch__ = {
    "goToUser": goToUser,
    "removeSearchQuery": removeSearchQuery,
    "clearSearchHistory": clearSearchHistory
}

def dispatch(name, *args):

    if (
        not (action := __dispatch__.get(name)) or
        not callable(action)
    ):
        raise Exception(f"Invalid script '{name}'")
    action(*args)


if __name__ == "__main__":
    dispatch(*argv[1:])

