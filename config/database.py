from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.ConfigService import config

if config.db_connection == 'sqlite':
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
else:
    username = config.db_username
    password = config.db_password
    port = config.db_port
    host = config.db_host
    database = config.db_database
    SQLALCHEMY_DATABASE_URL = URL.create(
        drivername="mysql+mysqlconnector",
        username=username,
        password=password,  # plain (unescaped) text
        host=host,
        database=database,
        port=port
    )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=config.show_query
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
