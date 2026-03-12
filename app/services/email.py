

import smtplib
from email.mime.text import MIMEText

# SENDER_EMAIL = "testsumit19@gmail.com"     # your Gmail address
# APP_PASSWORD = "dyld bnbm auks eopc"       # your Gmail App Password (not normal password)

SENDER_EMAIL = "aaswacontact@gmail.com"     # your Gmail address
APP_PASSWORD = "gnjy cotv stwo lsla"    

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


def send_reward_claim_email(
    to_email: str,
    username: str,
    reward_name: str,
    token: str,
    address: str,
    postal_code: str,
    contact_no: str,
    claim_type: str
):

    if claim_type == "winning":
        category = "Winner reward category"
    else:
        category = "Participation reward category"

    subject = f"Congratulations {username}! 🎉 You are a Winner on Edangal"

    body = f"""
Subject: Congratulations {username}! 🎉 You are a Winner on Edangal

Dear {username},

Congratulations 🎉

You have been selected as a winner on the Edangal platform under the {category}.
Your gift is ready to be dispatched.

Please confirm the following details:

Gift: {reward_name}
Token: {token}

Delivery Address:
{address}

PIN - {postal_code}

Contact: {contact_no}
Email: {to_email}

🔔 Action Required
Kindly reply with "CONFIRMED" if all details are correct.

For any corrections, please mention the updated information in your reply.

Once confirmed, we will proceed with dispatch through our delivery partner.

Thank you for being a valued member of Edangal.
Best wishes for upcoming lucky draws!

Warm regards,
Team Edangal

🌐 www.edangal.com
📧 gift@edangal.com
"""

    send_email(to_email, subject, body)