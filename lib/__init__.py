# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, unicode_literals


_folders_schema_ = {
    "livestreams": {
        "": {
            "id": 30004,
            "action": "livestreams"
        },
        "featured": {
            "id": 30007,
            "action": "featured"
        }
    },
    "categories": {
        "": {
            "id": 30006,
            "action": "categories"
        },
        "search": {
            "id": 30006,
            "action": "search_categories"
        }
    },
    "users": {
        "recommended": {
            "id": 30009,
            "action": "recommended"
        },
        "search": {
            "id": 30003,
            "action": "search_users"
        }
    },
    "search": {
        "": {
            "id": 30002
        }
    }
}


_home_folders_ = (
    {"type": "livestreams", "style": "featured"},
    {"type": "users", "style": "recommended"},
    {"type": "livestreams"},
    {"type": "categories"},
    {"type": "search"}
)


_subfolders_defaults_ = ("users", "categories")

