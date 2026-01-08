import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def send_otp(destination):
    otp = str(random.randint(100000, 999999))
    if "@" in destination:
        msg = MIMEText(f"Your OTP is: {otp}")
        msg["Subject"] = "AI Doctor OTP"
        msg["From"] = os.getenv("SMTP_USER")
        msg["To"] = destination

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
            server.send_message(msg)
    else:
        # Implement SMS sending logic here using a service like Twilio
        pass
    return otp

def verify_otp(input_otp, actual_otp):
    return input_otp == actual_otp
