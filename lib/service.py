# -*- coding: utf-8 -*-


from requests import Session, Timeout

from iapc import Service, public

from tools import makeDataDir, getSetting, getLanguage, containerRefresh

from dlive.graphql import GraphQLError, queries
from dlive.utils import Cache


# ------------------------------------------------------------------------------
# Categories

class Categories(Cache, key="backendID"):

    missing = {
        "backendID": "-1",
        "title": "",
        "imgUrl": "",
        "watchingCount": 0
    }

    def __init__(self, data=None):
        super().__init__(data["list"] if data else [])

    def update(self, data):
        return super().update(data["list"])


# ------------------------------------------------------------------------------
# DLiveSession

class DLiveSession(Session):

    def __init__(self, logger, headers=None):
        super().__init__()
        self.logger = logger.getLogger("session")
        if headers:
            self.headers.update(headers)
        self.__setup__()

    def __setup__(self):
        if (timeout := getSetting("timeout", float)) <= 0.0:
            self.timeout = None
        else:
            self.timeout = (((timeout - (timeout % 3)) + 0.05), timeout)
        self.logger.info(f"timeout: {self.timeout}")

    def request(self, *args, **kwargs):
        response = super().request(*args, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response


# ------------------------------------------------------------------------------
# DLiveService

class DLiveService(Service):

    __headers__ = {}

    __url__ = "https://graphigo.prd.dlive.tv/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__session__ = DLiveSession(self.logger, headers=self.__headers__)
        self.__categories__ = Categories(self.query("categories", first=48))
        makeDataDir()

    def start(self, **kwargs):
        self.logger.info("starting...")
        self.__setup__()
        self.serve(**kwargs)
        self.logger.info("stopped")

    def onSettingsChanged(self):
        self.__setup__()
        containerRefresh()

    # --------------------------------------------------------------------------

    def __setup__(self):
        self.__first__ = getSetting("first", int)
        self.__nsfw__ = getSetting("nsfw", bool)
        self.__language__ = getLanguage()
        self.__session__.__setup__()

    # --------------------------------------------------------------------------

    def query(self, query, key=None, **kwargs):
        query, keys = queries[query]
        json = {"query": query}
        if kwargs:
            json.update(variables=kwargs)
        response = self.__session__.post(self.__url__, json=json).json()
        data = response.get("data", None)
        errors = response.get("errors", None)
        if errors is not None:
            error = GraphQLError(errors)
            if data is None:
                raise error
            else:
                self.logger.warning(f"query error [{error}]")
        for k in keys:
            data = data[k]
        if key is not None:
            return [item[key] for item in data]
        return data

    # public api ---------------------------------------------------------------

    @public
    def stream(self, **kwargs):
        return self.query("stream", **kwargs)

    @public
    def user(self, **kwargs):
        return self.query("user", first=self.__first__, **kwargs)

    @public
    def category(self, **kwargs):
        # unfortunately I couldn't find a way to get 1 category from its id
        return self.__categories__[kwargs["categoryID"]]

    # --------------------------------------------------------------------------

    @public
    def featured(self, **kwargs):
        return self.query(
            "featured", key="item", userLanguageCode=self.__language__, **kwargs
        )

    @public
    def recommended(self, **kwargs):
        return self.query("recommended", key="user", **kwargs)

    @public
    def streams(self, **kwargs):
        return self.query(
            "streams", first=self.__first__, showNSFW=self.__nsfw__, **kwargs
        )

    @public
    def categories(self, **kwargs):
        data = self.query("categories", first=self.__first__, **kwargs)
        self.__categories__.update(data)
        return data

    @public
    def search_users(self, **kwargs):
        self.logger.info(f"search_users(kwargs={kwargs})")
        result = self.query("search_users", first=self.__first__, **kwargs)
        result["list"] = [item.get("creator", item) for item in result["list"]]
        return result

    @public
    def search_categories(self, **kwargs):
        data = self.query("search_categories", first=self.__first__, **kwargs)
        self.__categories__.update(data)
        return data


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    DLiveService().start()

