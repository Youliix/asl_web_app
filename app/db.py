import os
import psycopg2
import logging

dbname = os.getenv('DATABASE_NAME')
user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
host = os.getenv('DATABASE_HOST')
port = os.getenv('DATABASE_PORT')


def get_db_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    except Exception as e:
        print(f"Failed to establish a connection: {e}")
    finally:
        return connection


def check_db_connection():
    try :
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(version)
        cur.close()
        connection.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(connection):
            cur.close()
            connection.close()


def db_init():
    try: 
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(open("app/static/db/database_schema.sql", "r").read())
        connection.commit()
        print("Database has been initialized")
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(connection):
            cursor.close()
            connection.close()


def save_image_content(img, keypoints, prediction):
    try:
        image = img.read()
        keypoints = [coord for point in keypoints for coord in point.values()]
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO posts (label, image, keypoints) VALUES (%s, %s, %s)", (prediction, image, keypoints))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(connection):
            cursor.close()
            connection.close()
