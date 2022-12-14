from bs4 import BeautifulSoup, Tag
from UtilityFunctions import fetch_web_data


class BechdelTestDotCom(object):

    URL = "https://bechdeltest.com/?list=all"

    def __init__(self) -> None:
        self.movies = self.__extract_movies(self.__get_data())

    def __get_data(self) -> BeautifulSoup:
        """Fetches data from bechdeltest.com safely and returns it in a BeautifulSoup

        Args:
            url (str): The url to fetch from

        Raises:
            SystemExit: Raises an exception if data retrieval fails

        Returns:
            BeautifulSoup: A BeautifulSoup object carrying the whole data of the website
        """
        page = fetch_web_data(self.URL)

        return BeautifulSoup(page.content, features="lxml")

    def __extract_movies(self, soup: BeautifulSoup) -> "list[Tag]":
        """Takes a soup object from bechdeltest.com and extracts all movies from the soup

        Args:
            soup (BeautifulSoup): A soup object of the main documentation

        Returns:
            list[Tag]: A list of html tags that carry the name and bechdel score of a movies
        """
        return soup.find_all("div", {"class": "movie"})

    def process_movie(self, movie: Tag) -> dict:
        """Takes a html tag carrying movies name and bechdel score and extracts it

        Args:
            in_movie (Tag): A html tag that carry the name and bechdel score of a movie

        Returns:
            dict: A dictionary carrying the name and bechdel score of a movie
        """
        res_dict = {}
        # Separate the tag into link tags since it is comprised of three of those
        a_tags = movie.find_all("a")
        # The second link tag carries the name of the movie
        res_dict["movie_name"] = a_tags[1].text
        # The alt element of the image in the first link tag carries the bechdel score
        # Use python magic to transform "[[3]]" into "3"
        res_dict["bechdel_score"] = int(
            "".join(filter(str.isdigit, (a_tags[0].find("img")["alt"]))))

        return res_dict

    def process_all_movies(self) -> "list[dict]":
        """Processes all movies it can find on the bechdeltest website

        Returns:
            list[dict]: A list of dictionaries carrying the name and bechdel score of the movies
        """
        res_list = []
        for movie in self.movies:
            try:
                res_list.append(self.process_movie(movie=movie))
            except:
                continue

        return res_list
