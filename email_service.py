import smtplib
from email.message import EmailMessage

from config import (
    SENDER_EMAIL,
    SENDER_PASSWORD,
    RECEIVER_EMAIL
)


def send_post_email(topic, pdf_bytes):

    if not SENDER_EMAIL:
        raise ValueError("SENDER_EMAIL is missing in .env")

    if not SENDER_PASSWORD:
        raise ValueError("SENDER_PASSWORD is missing in .env")

    if not RECEIVER_EMAIL:
        raise ValueError("RECEIVER_EMAIL is missing in .env")

    # Create email
    message = EmailMessage()

    message["Subject"] = f"Your LinkedIn Post - {topic}"
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    message.set_content(
        f"""
Hello,

Your AI-generated LinkedIn post has been approved.

Topic:
{topic}

The approved LinkedIn post is attached as a PDF.

Regards,
AI LinkedIn Post Generator
"""
    )

    # Attach PDF
    message.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename="LinkedIn_Post.pdf"
    )

    # Connect to Gmail SMTP
    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=30
    ) as server:

        server.login(
            SENDER_EMAIL,
            SENDER_PASSWORD.replace(" ", "")
        )

        server.send_message(message)