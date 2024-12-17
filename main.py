# Imports 
from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import numpy as np

#  connect to db and create cursor
db = sqlite3.connect("Top-250-movies.db")
cursor = db.cursor()
# create table if table does not exist. 
try:
    cursor.execute("CREATE TABLE movies (id INTEGER PRIMARY KEY, title varchar(255) NOT NULL UNIQUE, description varchar(255), rating FLOAT NOT NULL, BestRating FLOAT NOT NULL , LowestRating FLOAT NOT NULL, RatingCount INTEGER NOT NULL, ContentRating varchar(50) NOT NULL, genre varchar(255) NOT NULL, duration INTEGER NOT NULL, url varchar(255) NOT NULL )")
except Exception as error:
    if 'already exists' in str(error):
        pass
    else:
        print(error)

# URL for top 250 movies list from imdb
TOP_250_MOVIES = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"

# sets the session header to get access 
with requests.Session() as se:
    se.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en"
    }

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
        case "load saved":
            with open('output.json','r') as file:
                json_data = json.load(file)
        # updates the db based on data scraped (local/url)
        case "update":
            try:

                numpy_array = np.array(json_data["itemListElement"])
                print(numpy_array[0]['item']['url'])
                # for i in json_data["itemListElement"]:
                    # print(i)
            except Exception as error:
                print(error)
        # creates table in db if not present
        case "create table":
            pass