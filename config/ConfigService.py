from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigService(BaseSettings):
    app_name: str = "Awesome API"
    app_env: str = "local"

    # APP MAILS
    app_admin_email: str = "naderounmu@altaracredit.com"
    app_technology_mail: str = "naderounmu@altaracredit.com"

    # DATABASE
    db_connection: str
    db_port: int
    db_host: str
    db_database: str
    db_username: str
    db_password: str
    # MAIL
    mail_driver: str
    mail_host: str
    mail_port: str
    mail_username: str
    mail_password: str
    mail_encryption: str
    mail_from_address: str
    mail_from_name: str

    # SES
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
    aws_bucket: str
    aws_url: str

    mail_template_folder: str = '../templates/email'

    model_config = SettingsConfigDict(env_file=".env")


config = ConfigService()
