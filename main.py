# Imports 
from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import numpy as np

def time(duration):
    try:
        duration = duration.strip("PTM")
        duration = duration.split("H")
        if len(duration) == 1:
            return int(duration[0])
        if bool(duration[1]):
            return int(duration[0]) * 60 + int(duration[1])
        else:
            return int(duration[0]) * 60
    except Exception as error:
        print("time function error " + str(error))
#  connect to db and create cursor
db = sqlite3.connect("Top-250-movies.db")
cursor = db.cursor()
# create table if table does not exist. 
try:
    cursor.execute("CREATE TABLE movies (id INTEGER PRIMARY KEY, title varchar(255) NOT NULL UNIQUE, year INTEGER NOT NULL , description varchar(255), rating FLOAT NOT NULL,"
                    "bestRating FLOAT NOT NULL , lowestRating FLOAT NOT NULL, ratingCount INTEGER NOT NULL, contentRating varchar(50) NOT NULL, "
                    "genre varchar(255) NOT NULL, duration INTEGER NOT NULL, url varchar(255) NOT NULL )")
except Exception as error:
    if 'already exists' in str(error):
        pass
    else:
        print(error)

# URL for top 250 movies list from imdb
TOP_250_MOVIES = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"

movie_obj_list = []

# sets the session header to get access 
with requests.Session() as se:
    se.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en"
    }

# The movie class that creates an object for each movie
class Movie:
    def __init__(self, id, title, year, description, rating, best_rating, lowest_rating, rating_count, content_rating, genre, duration, url):
        self.id = int(id) 
        self.title = title
        self.year = int(year)
        self.description = description
        self.rating = float(rating)
        self.best_rating = float(best_rating)
        self.lowest_rating = float(lowest_rating)
        self.rating_count = int(rating_count)
        self.content_rating = content_rating
        self.genre = genre
        self.duration = int(duration)
        self.url = url



while True:
    user_input = input("What would you like to do: ")

    match user_input:
        # Scrapes the url for data and outputs to json file for local storage
        case "refresh":
            response = se.get(TOP_250_MOVIES)
            website_html = response.text

            soup = BeautifulSoup(website_html, "html.parser")
            movie_list = soup.find('script', {"type": "application/ld+json"})
            json_string = movie_list.string.strip()
            json_data = json.loads(json_string)

            print(json_data)
            with open('output.json','w+',encoding='utf-8') as file:
                json.dump(json_data,file,indent=4)
        # load data from local save
        case "load":
            with open('output.json','r') as file:
                json_data = json.load(file)
        # updates the db based on data scraped (local/url)
        case "update":
            try:

                numpy_array = np.array(json_data["itemListElement"])
                # print(numpy_array[0]['item'])
                for i in range(len(numpy_array)):
                    if i == 203:
                        pass
                    movie = numpy_array[i]['item']
                    ratings = movie['aggregateRating']
                    content_rating = movie.get('contentRating', 'N/A')
                    
                    # print(movie)
                    movie_obj_list.append(Movie(
                        i,
                        movie['name'],
                        0,
                        movie['description'],
                        ratings['ratingValue'],
                        ratings['bestRating'],
                        ratings['worstRating'],
                        ratings['ratingCount'],
                        content_rating,
                        movie['genre'],
                        time(movie['duration']),
                        movie['url']
                    ))
                    # print(movie['name'])
                    # a == Movie(
                    #     i,
                    #     movie['name'],
                    #     0,
                    #     movie['description'],
                    #     movie['rating'],
                    #     movie['bestRating'],
                    #     movie['worstRating'],
                    #     movie['ratingCount'],
                    #     movie['contentRating'],
                    #     movie['genre'],
                    #     time(movie['duration']),
                    #     movie['url']
                    # )
                print(movie_obj_list[0].title)
                    
            except Exception as error:
                print(error)
        # creates table in db if not present
        case "create table":
            pass