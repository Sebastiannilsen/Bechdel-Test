from requests import get
from UtilityFunctions import fetch_web_data


class OMDbWrapper(object):

    URL = "http://www.omdbapi.com/?apikey={}&t={}"
    API_KEY = "f286551b"

    def __init__(self) -> None:
        pass

    def get_all_movie_data(self, movie_title: str) -> dict:
        """Fetches all available data on a movie from the OMDb database

        Args:
            movie_title (str): The title of the movie to be queried

        Returns:
            dict: The return object can be seen in further detail in the OMDb database API documentation
        """
        return fetch_web_data(self.URL.format(self.API_KEY, movie_title)).json()

    def get_movie_rating_data(self, movie_title: str) -> dict:
        """Extracts only the rating data on a movie from the OMDb database

        Args:
            movie_title (str): The title of the movie to be queried

        Returns:
            dict: A dictionary carrying all available rating data
        """
        ret_dict = {}
        for rating in self.get_all_movie_data(movie_title=movie_title)["Ratings"]:
            ret_dict[rating["Source"]] = rating["Value"]

        return ret_dict


ow = OMDbWrapper()

print(ow.get_movie_rating_data("Batman"))
