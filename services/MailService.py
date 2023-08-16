from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import BackgroundTasks
from config.ConfigService import config
import os
from fastapi import File, UploadFile
from typing import Optional
from pathlib import Path

class MailService:

    @classmethod
    async def send_email_async(cls, subject: str, email_to: str, body: dict, template: str,
                               attachment: Optional[UploadFile | None] = File()):
        # Save the uploaded file to a local directory


        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=body,
            subtype=MessageType.html,
            attachments=[attachment]
        )

        mailer = cls.get_mailer()
        if template.endswith(".html") is False:
            template_name = f"{template}.html"
        else:
            template_name = template

        cls.email_template_exists(template_name)

        await mailer.send_message(message, template_name=template_name)

    @classmethod
    async def send_email_sync(cls, subject: str, email_to: str, body: dict):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=body,
            subtype=MessageType.html,
        )

        mailer = cls.get_mailer()

        await mailer.send_message(message, template_name='sample-email.html')

    @classmethod
    def get_mailer(cls):
        email_template_dir = cls.get_emails_template_directory()

        mail_config = ConnectionConfig(
            MAIL_USERNAME=config.mail_username,
            MAIL_PASSWORD=config.mail_password,
            MAIL_FROM=config.mail_from_address,
            MAIL_PORT=config.mail_port,
            MAIL_SERVER=config.mail_host,
            MAIL_FROM_NAME=config.mail_from_name,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=email_template_dir
        )
        return FastMail(mail_config)

    @classmethod
    def get_emails_template_directory(cls):
        return os.path.join(config.template_dir, "emails")

    @classmethod
    def email_template_exists(cls, template_name):
        email_template_dir = cls.get_emails_template_directory()
        path = os.path.join(email_template_dir, template_name)
        if os.path.exists(path):
            return True
        else:
            raise Exception("Invalid template name provided")
