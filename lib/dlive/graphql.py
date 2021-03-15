# -*- coding: utf-8 -*-


# ------------------------------------------------------------------------------
# GraphQLError

class GraphQLError(Warning):

    __unknown__ = "Unknown error ({})"

    def __init__(self, errors):
        try:
            error = errors[0]
        except IndexError:
            message = self.__unknown__.format("empty 'errors' list")
        else:
            if isinstance(error, dict):
                try:
                    message = error["message"]
                except KeyError:
                    message = self.__unknown__.format("missing error 'message'")
            else:
                message = str(error)
            if not message:
                message = self.__unknown__.format("empty error 'message'")
        super().__init__(message)


# queries ----------------------------------------------------------------------

queries = {

    "stream": (
        """
        query _stream_($username: String!) {
            user(username: $username) {
                username
                displayname
                livestream {
                    permlink
                    ageRestriction
                    thumbnailUrl
                    title
                    createdAt
                    watchingCount
                    language {
                        backendID
                        code
                    }
                    category {
                        backendID
                        title
                        imgUrl
                        coverImgUrl
                        watchingCount
                    }
                    creator {
                        username
                        displayname
                        avatar
                    }
                }
            }
        }
        """,
        ("user",)
    ),

    "user": (
        """
        query _user_($username: String!, $first: Int, $after: String = "-1") {
            user(username: $username) {
                username
                displayname
                livestream {
                    permlink
                    ageRestriction
                    thumbnailUrl
                    title
                    createdAt
                    watchingCount
                    language {
                        backendID
                        code
                    }
                    category {
                        backendID
                        title
                        imgUrl
                        coverImgUrl
                        watchingCount
                    }
                    creator {
                        username
                        displayname
                        avatar
                    }
                }
                pastBroadcasts(first: $first, after: $after) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    list {
                        permlink
                        ageRestriction
                        length
                        thumbnailUrl
                        title
                        createdAt
                        viewCount
                        playbackUrl
                        #resolution {
                        #    resolution
                        #    url
                        #}
                        language {
                            backendID
                            code
                        }
                        category {
                            backendID
                            title
                            imgUrl
                            coverImgUrl
                            watchingCount
                        }
                        creator {
                            username
                            displayname
                            avatar
                        }
                    }
                }
            }
        }
        """,
        ("user",)
    ),

    "streams": (
        """
        query _streams_($first: Int, $after: String = "-1",
                        $categoryID: Int = 0, $showNSFW: Boolean = false) {
            livestreams(input: {first: $first, after: $after,
                                categoryID: $categoryID, showNSFW: $showNSFW,
                                order: TRENDING}) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                list {
                    permlink
                    ageRestriction
                    thumbnailUrl
                    title
                    createdAt
                    watchingCount
                    language {
                        backendID
                        code
                    }
                    category {
                        backendID
                        title
                        imgUrl
                        coverImgUrl
                        watchingCount
                    }
                    creator {
                        username
                        displayname
                        avatar
                    }
                }
            }
        }
        """,
        ("livestreams",)
    ),

    "featured": (
        """
        query _featured_($userLanguageCode: String) {
            carousels(count: 8, userLanguageCode: $userLanguageCode) {
                item {
                    ... on Livestream {
                        permlink
                        ageRestriction
                        thumbnailUrl
                        title
                        createdAt
                        watchingCount
                        language {
                            backendID
                            code
                        }
                        category {
                            backendID
                            title
                            imgUrl
                            coverImgUrl
                            watchingCount
                        }
                        creator {
                            username
                            displayname
                            avatar
                        }
                    }
                }
            }
        }
        """,
        ("carousels",)
    ),

    "recommended": (
        """
        query _recommended_ {
            globalInfo {
                recommendChannels(limit: 8) {
                    user {
                        username
                        displayname
                        avatar
                        followers {
                            totalCount
                        }
                    }
                }
            }
        }
        """,
        ("globalInfo", "recommendChannels")
    ),

    "categories": (
        """
        query _categories_($first: Int, $after: String = "-1") {
            categories(input: {first: $first, after: $after}) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                list {
                    backendID
                    title
                    imgUrl
                    coverImgUrl
                    watchingCount
                }
            }
        }
        """,
        ("categories",)
    ),

    "search_users": (
        """
        query _search_users_($text: String!, $first: Int, $after: String = "-1") {
            search(text: $text) {
                allUsers(first: $first, after: $after) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    list {
                        ... on Livestream {
                            creator {
                                username
                                displayname
                                avatar
                                followers {
                                    totalCount
                                }
                            }
                        }
                        ... on User {
                            username
                            displayname
                            avatar
                            followers {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
        """,
        ("search", "allUsers")
    ),

    "search_categories": (
        """
        query _search_categories_($text: String!, $first: Int, $after: String = "-1") {
            search(text: $text) {
                liveCategories(first: $first, after: $after) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    list {
                        backendID
                        title
                        imgUrl
                        coverImgUrl
                        watchingCount
                    }
                }
            }
        }
        """,
        ("search", "liveCategories")
    ),

}

