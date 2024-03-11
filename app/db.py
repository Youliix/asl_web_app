import os
import psycopg2

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
    connection = get_db_connection()
    cursor = connection.cursor()
    try :
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(version)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def db_init():
    connection = get_db_connection()
    cursor = connection.cursor()
    try: 
        cursor.execute(open("app/static/db/database_schema.sql", "r").read())
        connection.commit()
        print("Database has been initialized")
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def save_image_content(img, keypoints, prediction):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        img = img.read()
        keypoints = [coord for point in keypoints for coord in point.values()]
        cursor.execute("INSERT INTO images (image) VALUES (%s)", (img,))
        cursor.execute("SELECT id FROM images WHERE image = %s", (img,))
        image_id = cursor.fetchone()
        cursor.execute("INSERT INTO keypoints (image_id, label, keypoints) VALUES (%s, %s, %s)", (image_id, prediction, keypoints,))
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()
