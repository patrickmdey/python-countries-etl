import pandas as pd
import dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import openpyxl
import json

class EmailSender:
    """Class that contains the email sender credentials
    Args:
        email_usr (str): Email address of the sender
        email_pass (str): Password of the email address of the sender
        email_server (str): SMTP server of the email address of the sender
    """
    SMTP_PORT = 587

    def __init__(self, email_usr, email_pass, email_server):
        self.email = email_usr
        self.password = email_pass
        self.server = email_server

def send_email(email_sender: EmailSender,recipients_list, subject, body, attachment_path=None):
    """Creates an email that has the countries.xlsx file attached and sends it to the recipients
    Args:
        email_sender (EmailSender): EmailSender object with the email sender credentials
        recipient_email (list of str): Email addresses of the recipients
        subject (str): Email subject
        body (str): Email body
        attachment_path (str, optional): Path of the file to attach
    """

    """Sets the email parts"""
    message = MIMEMultipart()
    message['From'] = email_sender.email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    wb = openpyxl.load_workbook(attachment_path)

    """Attatch the file to the email"""
    attachment = MIMEApplication(open(attachment_path, 'rb').read())
    attachment.add_header('Content-Disposition', 'attachment', filename=attachment_path)
    message.attach(attachment)

    with smtplib.SMTP(email_sender.server, email_sender.SMTP_PORT) as server:
        server.starttls()
        server.login(email_sender.email, email_sender.password)

        for recipient_email in recipients_list:
            message['To'] = recipient_email 
            # Connect to the SMTP server and send the email
            server.sendmail(email_sender.email, recipient_email, message.as_string())

if __name__ == "__main__":
    """Receive the email configuration from the email_config.json file and sends the email
        it creates the countries.xlsx file form the database in case it gets updated
    """
    if not os.path.exists("email_config.json"):
        print("Error: email_config.json file not found")
        exit(0)
    with open("email_config.json", "r") as config_f:
        config = json.load(config_f)
        recipient_email = config["recipient"]
        subject = config["subject"]
        body = config["body"]

        if recipient_email is None or subject is None or body is None:
            print("Error: email_usr, email_pass or email_server is None")
            exit(0)

        dotenv.load_dotenv()
        postgresql_url = os.getenv("POSTGRESQL_URL")
        countries_df = pd.read_sql_table("countries", postgresql_url)
        countries_df.to_excel("countries.xlsx", sheet_name="Paises", index=False)

        """Receives the email sender credentials from the .env file"""
        email_usr = os.getenv("EMAIL_USR")
        email_pass = os.getenv("EMAIL_PASS")
        email_server = os.getenv("EMAIL_SERVER") # for example: smtp.gmail.com for Gmail

        if email_usr is None or email_pass is None or email_server is None:
            print("Error: email_usr, email_pass or email_server is None")
            exit(0)

        email_sender = EmailSender(email_usr, email_pass, email_server)

        send_email(email_sender, recipient_email, subject, body, "countries.xlsx")

    config_f.close()
    
