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
            "label": 30002,
            "art": {"poster": "DefaultAddonsSearch.png"}
        },
        "users": {
            "label": 30003,
            "kwargs": {"query": "search_users"},
            "art": {"poster": "DefaultArtist.png"}
        },
        "categories": {
            "label": 30006,
            "kwargs": {"query": "search_categories"},
            "art": {"poster": "DefaultGenre.png"}
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


search_queries = {
    "search_users": {
        "action": "user",
        "category": 30003
    },
    "search_categories": {
        "action": "category",
        "category": 30006
    }
}

