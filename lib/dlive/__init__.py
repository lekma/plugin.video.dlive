# -*- coding: utf-8 -*-


__schema__ = {

    "streams": {
        "": {
            "label": 30004
        },
        "featured": {
            "label": 30007,
            "action": "featured"
        }
    },

    "categories": {
        "": {
            "label": 30006
        }
    },

    "users": {
        "recommended": {
            "label": 30009,
            "action": "recommended"
        }
    },
    "search": {
        "": {
            "label": 30002
        },
        "users": {
            "label": 30003,
            "action": "search_users"
        },
        "categories": {
            "label": 30006,
            "action": "search_categories"
        }
    }

}


home = (
    {"type": "streams", "style": "featured"},
    {"type": "users", "style": "recommended"},
    {"type": "streams"},
    {"type": "categories"},
    {"type": "search"}
)


styles = {
    "search": ("users", "categories")
}

