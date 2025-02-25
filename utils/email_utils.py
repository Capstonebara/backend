from fastapi_mail import FastMail, MessageSchema, MessageType
from config.email_config import conf
import os
from jinja2 import Environment, FileSystemLoader
from typing import List

async def send_email(subject: str, recipients: list, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print("Test emails sent successfully")
    except Exception as e:
        print(f"Failed to send emails: {str(e)}")

# Set up Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')
jinja_env = Environment(loader=FileSystemLoader(template_dir))

async def send_local(subject: str, recipients: list[dict]):
    fm = FastMail(conf)
    template = jinja_env.get_template('personalized_link_local.html')


    for recipient in recipients:
        personalized_link = f"https://fptuaiclub.me/?email={recipient['email']}"

        # Render the template with personalized data
        html_content = template.render(
            recipient_name=recipient.get('name', 'Valued Customer'),
            recipient_email=recipient['email'],
            personalized_link=personalized_link
        )

        message = MessageSchema(
            subject=subject,
            recipients=[recipient['email']],
            body=html_content,
            subtype=MessageType.html
        )

        try:
            await fm.send_message(message)
        except Exception as e:
            print(f"Failed to send emails to {recipient}: {str(e)}")


async def send_personalized_emails(subject: str, recipients: list[dict]):
    fm = FastMail(conf)
    template = jinja_env.get_template('personalized_link.html')


    for recipient in recipients:
        personalized_link = f"https://fptuaiclub.me/?email={recipient['email']}"

        # Render the template with personalized data
        html_content = template.render(
            recipient_name=recipient.get('name', 'Valued Customer'),
            recipient_email=recipient['email'],
            personalized_link=personalized_link
        )

        message = MessageSchema(
            subject=subject,
            recipients=[recipient['email']],
            body=html_content,
            subtype=MessageType.html
        )

        try:
            await fm.send_message(message)
        except Exception as e:
            print(f"Failed to send emails to {recipient}: {str(e)}")
