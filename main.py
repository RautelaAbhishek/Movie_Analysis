# Imports 
from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from collections import Counter

# variables
movie_obj_list = []
##  connect to db and create cursor
db = sqlite3.connect("movies.db")
cursor = db.cursor()

# Functions
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


# create table if table does not exist. 
def createTable(table):
    try:
        cursor.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, title varchar(255) NOT NULL UNIQUE, year INTEGER NOT NULL , description varchar(255), rating FLOAT NOT NULL,"
                        "bestRating FLOAT NOT NULL , lowestRating FLOAT NOT NULL, ratingCount INTEGER NOT NULL, contentRating varchar(50) NOT NULL, "
                        "genre varchar(255) NOT NULL, duration INTEGER NOT NULL, url varchar(255) NOT NULL )")
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
createTable("movies")


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
        case "init":
            try:
                numpy_array = np.array(json_data["itemListElement"])
                # loop through the movie list and append movie_ob_list with newly created movie objects
                for i in range(len(numpy_array)):
                    movie = numpy_array[i]['item']
                    ratings = movie['aggregateRating']
                    # some movies are missing content rating so this sets those to N/A
                    content_rating = movie.get('contentRating', 'N/A')
                    try:
                        cursor.execute("INSERT INTO movies (id, title, year, description, rating, bestRating, lowestRating, ratingCount, contentRating, genre, duration, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(
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
                        db.commit()
                    except sqlite3.IntegrityError as error:
                        print(error)
            except Exception as error:
                print(error)
        # updates the db based on data scraped (local/url)
        case "update":
            try:
                numpy_array = np.array(json_data["itemListElement"])
                # loop through the movie list and append movie_ob_list with newly created movie objects
                for i in range(len(numpy_array)):
                    # debugging tool to be deleted
                    if i == 203:
                        pass
                    # debugging tool to be deleted
                    movie = numpy_array[i]['item']
                    ratings = movie['aggregateRating']
                    # some movies are missing content rating so this sets those to N/A
                    content_rating = movie.get('contentRating', 'N/A')
                    # update the db with the new data
                    cursor.execute("UPDATE movies SET title = ?, year = ?, description = ?, rating = ?, bestRating = ?, lowestRating = ?, ratingCount = ?, contentRating = ?, genre = ?, duration = ?, url = ? WHERE id = ?",(
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
                        movie['url'],
                        i
                    ))
                    db.commit()
            except Exception as error:
                print(error)
        # creates table in db if not present
        case "test":
            print(movie_obj_list[0].title)

        case "exit":
            db.close()
            # Exit the program
            exit()

        # Drop the specified table and recreate it
        case "drop":
            table = input("Enter table name: ")
            try:
                # Drop the table
                cursor.execute(f"DROP TABLE {table}")
                db.commit()
                # Recreate the table
                createTable(table)
            except sqlite3.DatabaseError as error:
                print(error)
            

    # get the number of genres and list in histogram for possible comparison

        case "get genres":
            cursor.execute("SELECT genre FROM movies")
            genres = cursor.fetchall()
            genre_list = []
            for genre in genres:
                genre_split = genre[0].split(",")
                for genre_item in genre_split:
                    genre_item = genre_item.strip(' ')
                    genre_list.append(genre_item)

            # Count the occurrences of each genre
            genre_counts = Counter(genre_list)
            
            # Extract genres and their counts
            genres = list(genre_counts.keys())
            counts = list(genre_counts.values())
            
            # Set figure size
            plt.figure(figsize=(12, 8))
            # Create bar plot
            plt.bar(genres, counts)
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            # Add labels and title
            plt.xlabel('Genre')
            plt.ylabel('Count')
            plt.title('Distribution of Movie Genres')
            # informs user of the most common genre
            print(f"From the graph, we can observe that {genres[counts.index(max(counts))]} is the most common genre in the top 250 movies list.")
            # Show plot
            plt.show()
            