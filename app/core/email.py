from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import random

# مثال للإعدادات الصحيحة
conf = ConnectionConfig(
    MAIL_USERNAME = "your_email@gmail.com",
    MAIL_PASSWORD = "abcd efgh ijkl mnop", # الباسورد الـ 16 حرف اللي طلعته من جوجل (بدون مسافات أو بمسافات هيشتغل)
    MAIL_FROM = "your_email@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)
async def send_verification_email(email_to: str):
    otp = str(random.randint(100000, 999999))
    
    message = MessageSchema(
        subject="CORE System | Verification Code",
        recipients=[email_to],
        body=f"Your verification code is: {otp}. Do not share it.",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return otp