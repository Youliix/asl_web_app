import os
import psycopg2

from werkzeug.security import generate_password_hash, check_password_hash


dbname = os.getenv("DATABASE_NAME")
user = os.getenv("DATABASE_USER")
password = os.getenv("DATABASE_PASSWORD")
host = os.getenv("DATABASE_HOST")
port = os.getenv("DATABASE_PORT")


def get_db_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
    except Exception as e:
        print(f"Failed to establish a connection: {e}")
    finally:
        return connection


def check_db_connection():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(version)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
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
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def get_user(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT firstname, lastname, rgpd_right FROM users WHERE id = %s",
            (id,),
        )
        row = cursor.fetchone()
        if row:
            return row
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def update_user(user):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE users SET firstname = %s, lastname = %s, rgpd_right = %s WHERE id = %s",
            (user['firstname'], user['lastname'], user['rgpd_right'], user['id']),
        )
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


# def delete_user(data):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     try:
#         cursor.execute(
#             "DELETE FROM users WHERE email = %s",
#             (data.email,),
#         )
#         connection.commit()
#     except (Exception, psycopg2.Error) as error:
#         print("Error while connecting to PostgreSQL", error)
#     finally:
#         cursor.close()
#         connection.close()


def save_image_content(img, keypoints, prediction, user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        img = img.read()
        keypoints = [coord for point in keypoints for coord in point.values()]
        cursor.execute(
            "INSERT INTO predictions (image, keypoint,  prediction, user_id) VALUES (%s, %s, %s, %s)",
            (
                img,
                keypoints,
                prediction,
                user_id,
            ),
        )
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()
