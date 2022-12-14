import csv
import requests
import pandas as pd
from lxml import html
from UtilityFunctions import fetch_web_data


class BechdelTest(object):

    ALL_MOVIES_URL = 'https://imsdb.com/all-scripts.html'
    INDIVIDUAL_MOVIE_URL = 'https://imsdb.com/scripts/{}.html'

    def __init__(self) -> None:
        self.__list_of_female_names = self.__populate_list_of_female_names()
        self.__list_of_male_names = self.__populate_list_of_male_names()
        self.__list_of_movies = self.get_available_move_titles()

    def __populate_list_of_female_names(self) -> "list[str]":
        """Fetches all female names from the csv

        Returns:
            list[str]: A list of strings carrying female names
        """

        res_lis = []
        with open('name_gender.csv', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[1] == 'F' or (row[1] == 'M' and float(row[2]) < 1):
                    res_lis.append(row[0])
        return res_lis

    def __populate_list_of_male_names(self) -> "list[str]":
        """Fetches all male names from the csv

        Returns:
            list[str]: A list of strings carrying male names
        """

        res_lis = []
        with open('name_gender.csv', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[1] == 'M' or (row[1] == 'F' and float(row[2]) < 1):
                    res_lis.append(row[0])
        return res_lis

    def __is_female_name(self, name: str) -> bool:
        """Check if the name is in the list of female names

        Args:
            name (str): A string carrying a name

        Returns:
            bool: A bool which says if name is male or not
        """
        #capitalize the first letter of the name
        name = name.strip()
        name = name[0].upper() + name[1:].lower()
        return name in self.__list_of_female_names

    def __is_male_name(self, name: str) -> bool:
        """Check if the name is in the list of male names

        Args:
            name (str): A string carrying a name

        Returns:
            bool: A bool which says if name is male or not
        """
        return name.strip().capitalize() in self.__list_of_male_names       

    def get_available_move_titles(self) -> "list[str]":
        """Scrapes imsdb for all of its movie names 

        Returns:
            list[str]: A list of strings of movie names
        """

        # get the movie names
        page = fetch_web_data(self.ALL_MOVIES_URL)
        tree = html.fromstring(page.content)

        # xpath expression to get all the text in the <a> tags
        movie_names = tree.xpath('//tr/td/p/a/text()')

        list_of_movies = []

        for movie in movie_names[1:]:
            list_of_movies.append(movie)

        return list_of_movies

    def get_movie_script(self, movie_name: str) -> "list[str]":
        """Takes a name of movie and returns its script from imsdb

        Args:
            movieName (str): A string carrying the movies name

        Returns:
            list[str]: A list of strings that are the script line for line
        """
        # replace spaces with hyphens
        movie_name = movie_name.replace(" ", "-")

        # get the movie names
        page = fetch_web_data(self.INDIVIDUAL_MOVIE_URL.format(movie_name))
        tree = html.fromstring(page.content)

        # xpath expression to get all the text in the <pre> tag
        movie_script = tree.xpath("//pre//text()")

        # remove "\n" and "\r" from the script
        movie_script = [line.replace("\n", "") for line in movie_script]
        movie_script = [line.replace("\r", "") for line in movie_script]

        # remove empty lines
        movie_script = [line for line in movie_script if line != ""]

        return movie_script

    def get_bechdel_score(self, movie_name: str) -> int:
        """Takes a string carrying a movie name and calculates the movies bechdel score

        Args:
            movie_name (str): A string carrying a movies name

        Returns:
            int: The calculated bechdel score
        """

        script = self.get_movie_script(movie_name=movie_name)
        # check if the script is empty
        if len(script) == 0:
            return "Invalid script"

        bechdel_score = 0
        # check if the movie is in the list of movies that pass the bechdel test
        # if yes, return the score and we dont need to check the script
        with open('knownMovies.csv', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row:
                    if row[0] == movie_name:
                        return row[1]

        # split the script into scenes each starting with ('INT.', 'EXT.', 'ESP.', 'EST.', 'SFX ', 'SFX:', 'VFX:')
        scenes = [[]]
        for line in script:
            if ('INT.' in line) or ('EXT.' in line) or ('ESP.' in line) or ('EST.' in line) or ('SFX ' in line) or ('SFX:' in line) or ('VFX:' in line):
                scenes.append([])
            scenes[-1].append(line)

        for scene in scenes:
            female_characters = []
            mentions_man = False
            score = 0
            for section in scene:
                # check if the section is a dialogue. Each dialogue is indented
                if section.startswith(" "):
                    # check if the sections contains "him", "he", "his" or any male name
                    if (" him " in section or " he " in section or " his " in section) or (any(self.__is_male_name(word) for word in section.split())):
                        mentions_man = True
                    # The talking person is capitalized
                    if section.isupper():
                        # check if the name is female and add it to the list
                        if self.__is_female_name(section.strip()):
                            female_characters.append(section.strip())
            # returns 1 if at one named women is in speaking in the scene
            if len(female_characters) > 0:
                score = 1
                # returns 2 if two or more women talk to each other in the same scene
                if len(female_characters) > 1:
                    score = 2
                    # returns 3 if the women didnt talk about a man
                    if not mentions_man:
                        score = 3
            # updates the bechdel score if the current scene outscored the previous ones
            if score > bechdel_score:
                bechdel_score = score

        # write the movie name and the result to a csv file
        with open('knownMovies.csv', mode='a', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([movie_name, bechdel_score])

        return bechdel_score

    def get_all_bechdel_scores(self) -> "list[dict]":
        ret_lis = []
        for movie in self.__list_of_movies:
            ret_lis.append(
                {"name": movie, "score": self.get_bechdel_score(movie)})
        return ret_lis


    def getMovieRating(self, movie_name: str) -> pd.DataFrame:

        # Access to OMDB api
        url = "http://www.omdbapi.com/?apikey=f286551b&t=" + movie_name
        # Store the result in json object
        result = requests.get(url).json()
        rate = []
        # get the rating of the corresponding movie
        if result['Response']=='True':
            if len(result['Ratings'])==3:
                ratingMovie = result['Ratings']
                sourceRate = []
                movieRate = []
                for i in range(len(ratingMovie)):
                    # Source of the rating
                    sourceRate.append(ratingMovie[i]['Source'])
                    # Value
                    movieRate.append(ratingMovie[i]['Value'])
                rate = pd.DataFrame(sourceRate, columns=['Sources'])
                rate.insert(1, 'Value', movieRate, True)
                return rate
            elif len(result['Ratings'])!=3:
                return rate
        elif result['Response']=='False':
            return rate