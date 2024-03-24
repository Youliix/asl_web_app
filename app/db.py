import os
import psycopg2

from werkzeug.security import generate_password_hash, check_password_hash
import logging

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
        logging.warning(f"Failed to establish a connection: {e}")
    finally:
        return connection


def check_db_connection():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logging.warning(version)
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error:
        logging.warning("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def db_init():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(open("app/static/db/database_schema.sql", "r").read())
        connection.commit()
        logging.warning("Database has been initialized")
    except (Exception, psycopg2.Error) as error:
        logging.warning("Error while connecting to PostgreSQL", error)
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
        logging.warning("Error while connecting to PostgreSQL", error)
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
        logging.warning("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM predictions WHERE user_id = %s", (user_id,))
        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,),
        )
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        logging.warning("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def get_user_pwd(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT password FROM users WHERE id = %s",
            (int(user_id),),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        logging.warning("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()


def update_password(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        user = get_user_pwd(data['id'])
        if not check_password_hash(user, data['oldPassword']):
            return {"error": "Mot de passe est incorrect.", "code": 400}
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (generate_password_hash(data['newPassword']), data['id']),
        )
        connection.commit()
        return {"message": "Mot de passe mis à jour.", "code": 200}
    except (Exception, psycopg2.Error) as error:
        logging.warning("Error while connecting to PostgreSQL", error)
        return {"error": "Une erreur est survenue lors de la mise à jour du mot de passe.", "code": 500}
    finally:
        cursor.close()
        connection.close()


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
        logging.warning("Error while connecting to PostgreSQL", error)
    finally:
        cursor.close()
        connection.close()
