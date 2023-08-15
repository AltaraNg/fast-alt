from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import BackgroundTasks
from config.ConfigService import config
import os


class MailService:

    @classmethod
    async def send_email_async(cls, subject: str, email_to: str, body: dict):
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
        email_template_dir = os.path.join(config.template_dir, "emails")

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
