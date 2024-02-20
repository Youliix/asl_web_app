from dotenv import load_dotenv
load_dotenv()

import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import psycopg2

dbname = os.getenv('DATABASE_NAME')
user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
host = os.getenv('DATABASE_HOST')
port = os.getenv('DATABASE_PORT')

email_sender = os.getenv('EMAIL_SENDER')
email_receiver = os.getenv('EMAIL_RECEIVER')
email_app_pwd = os.getenv('EMAIL_APP')


def collect_metrics():
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        curr = connection.cursor()
        
        curr.execute("SELECT pg_database_size(%s);", (dbname,))
        db_size_bytes = curr.fetchone()[0]
        total_space_bytes = 1 * 1024**3
        fill_percentage = (db_size_bytes / total_space_bytes) * 1000
        return fill_percentage
    except Exception as e:
        print(e)


def send_email(metrics):
    
    message = MIMEMultipart()
    message["From"] = email_sender
    message["To"] = email_receiver
    message["Subject"] = "Suivi de l'espace disque de la base de données."

    body = f"La base de données est remplie à {metrics:.2f}%. Merci de faire le nécessaire."

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()    
    try:
        server.login(email_sender, email_app_pwd)
        server.sendmail(email_sender, email_receiver, message.as_string())
        print("Email envoyé avec succès !")
    except smtplib.SMTPHeloError as error:
        print(f"Erreur lors de l'envoi de l'email : {str(error)}")
    finally:
        if server:
            server.quit()


def main():
    metrics = collect_metrics()
    if metrics:
        send_email(metrics)


if __name__ == "__main__":
    main()

