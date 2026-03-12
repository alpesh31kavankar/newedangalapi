

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
    lottery_id: int,
    address: str,
    postal_code: str,
    contact_no: str
):

    body = f"""
Hello {username},

Congratulations! 🎉

You have successfully submitted your reward claim on the Edangal platform.

Your reward details are as follows:

Reward: {reward_name}
Lottery ID: {lottery_id}

Delivery Details
---------------------------
Address:
{address}

Postal Code: {postal_code}
Contact Number: {contact_no}
Email: {to_email}
---------------------------

⚠️ Action Required

Please reply with "CONFIRMED" if the above details are correct.

If any details need correction, please reply with the updated information.

Once confirmed, we will proceed with dispatch through our delivery partner.

Thank you for participating in Edangal.

Best wishes for upcoming lucky draws!

Regards  
Edangal Team
www.edangal.com
"""

    send_email(to_email, "🎉 Edangal Reward Claim Confirmation", body)