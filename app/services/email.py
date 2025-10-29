

import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "testsumit19@gmail.com"     # your Gmail address
APP_PASSWORD = "dyld bnbm auks eopc"       # your Gmail App Password (not normal password)

def send_activation_email(to_email: str, activation_link: str):
    body = f"""
    Hello!

    Click this link to activate your account:
    {activation_link}

    Thank you!
    """
    send_email(to_email, "Activate Your Account", body)


def send_otp_email(to_email: str, otp_code: str, username: str):
    body = f"""
    Hello {username},

    Your OTP for password reset is: {otp_code}

    This OTP is valid for 10 minutes.
    If you did not request this, please ignore this email.

    Regards,
    Edangal.com
    """
    send_email(to_email, "Password Reset OTP", body)


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "no-reply@example.com"
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("Error sending email:", e)
