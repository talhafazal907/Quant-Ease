import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from dotenv import load_dotenv
import os
load_dotenv()


class Verify:
    """This class is responsible for Email verifications and Passwords reset"""
    def __init__(self):
            pass

    def send_token(self, email: str):
        """ This Function will take an email from the backend and send the token to the user email and also back0 for Confirmations"""
        try:
            code = str(random.randint(a = 1000, b= 9999))
            message = f"Wellcome to QuantEase. \nYou code is {code}"        
            msg = MIMEMultipart()
            msg['From'] = os.getenv("EMAIL_ADDRESS")
            msg['To'] =   email # You can change this to any recipient
            msg['Subject'] = "QuantEase Account Verification"
                
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
                server.send_message(msg)
                return code
        except Exception as e:
            return e
        
    def verify_token(self, email : str ,code : str):
        from db import DataBase_helper
        rs = DataBase_helper.verify(email, code)
        if rs:
              return 1
        else:
            return None 
        
