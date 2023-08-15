from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks
from config.ConfigService import config


class MailService:

    @classmethod
    async def send_email_async(cls, subject: str, email_to: str, body: dict):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype='html',
        )
        mailer = cls.get_mailer()
        await mailer.send_message(message, template_name='sample-email.html')

    @classmethod
    def get_mailer(cls):
        mail_config = ConnectionConfig(
            MAIL_USERNAME=config.mail_username,
            MAIL_PASSWORD=config.mail_password,
            MAIL_FROM=config.mail_from_address,
            MAIL_PORT=config.mail_port,
            MAIL_SERVER=config.mail_host,
            MAIL_FROM_NAME=config.mail_from_name,
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=config.template_folder
        )
        return FastMail(mail_config)
