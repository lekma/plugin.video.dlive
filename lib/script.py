# -*- coding: utf-8 -*-


from sys import argv

from tools import getAddonId

from dlive.utils import containerUpdate


__plugin_url__ = f"plugin://{getAddonId()}"


# user stuff ----------------------------------------------------------------

__user_url__ = f"{__plugin_url__}/?action=user&username={{}}"

def goToUser(username):
    containerUpdate(__user_url__.format(username))


# __main__ ---------------------------------------------------------------------

__dispatch__ = {
    "goToUser": goToUser
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

