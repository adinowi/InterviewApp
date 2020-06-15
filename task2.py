import sys
import sqlite3
import io

import flickrapi
from decouple import config
import requests
from PIL import Image
import matplotlib.pyplot as plt 
import numpy as np

API_KEY = config('API_KEY')
API_SECRET = config('API_SECRET')
get_photos = None

try:
    keyword = sys.argv[1]
    limit = int(sys.argv[2])
except Exception as error:
    get_photos = lambda : flickr.photos.getRecent(
                            extras='url_c')
    limit = 100
    print("Wrong arguments\n", error)

class DatabaseManager:
    def __init__(self):
        try:
            self.sqliteConnection = sqlite3.connect('flickr_db.db')
            self.__create_photos_table_if_not_exist()
        except sqlite3.Error as error:
            print("Failed init", error)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (self.sqliteConnection):
            self.sqliteConnection.close()  

    def __create_photos_table_if_not_exist(self):
        try:
            cursor = self.sqliteConnection.cursor()
            sql = 'create table if not exists Photos (id INTEGER PRIMARY KEY, photo BLOB NOT NULL)'
            cursor.execute(sql)
            self.sqliteConnection.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Failed to create photos table", error)

    def insert_photo(self, image_data):
        try:
            cursor = self.sqliteConnection.cursor()
            sqlite_insert_blob_query = "INSERT INTO Photos(photo) VALUES (?)"
            cursor.execute(sqlite_insert_blob_query, (image_data,))
            self.sqliteConnection.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Failed to insert photo", error)

    def find_most_red_colored_photo(self):
        try:
            cursor = self.sqliteConnection.cursor()
            sql_fetch_blob_query = "SELECT photo from Photos"
            cursor.execute(sql_fetch_blob_query)
            records = cursor.fetchall()
            red_count = 0
            best_image = None
            for row in records:
                img = Image.open(io.BytesIO(row[0])).convert('RGB')
                r, g, b = img.split()
                red_sum = np.array(r).sum()
                if best_image and red_sum > red_count:
                    red_count = red_sum
                    best_image = img
                
            plt.imshow(img)
            plt.show()
            cursor.close()
        except sqlite3.Error as error:
            print("Failed to find the most red-colored photo", error)


flickr=flickrapi.FlickrAPI(API_KEY,API_SECRET,cache=True)

if not get_photos:
    get_photos = lambda: flickr.walk(text=keyword,
                            tag_mode='all',
                            tags=keyword,
                            extras='url_c',
                            per_page=100,
                            sort="relevance")

photos = get_photos()
urls = []

for i, photo in enumerate(photos):
    if i >= limit:
        break
    try:
        url=photo.get('url_c')
        if url:
            urls.append(url)
    except Exception as e:
        print('failed to download image')
    

with DatabaseManager() as db_manager:
    for url in urls:
        data = requests.get(url).content
        db_manager.insert_photo(data)
    
    db_manager.find_most_red_colored_photo()