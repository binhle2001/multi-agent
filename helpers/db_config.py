from datetime import datetime
import logging
import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
# Định nghĩa các tham số kết nối
host = "192.168.0.107"
database = "multi_agent"
user = "root"
password = "password"
port = "5432"
# Define the database connection parameters
url_object = URL.create(
    "postgresql+pg8000",
    username=user,
    password=password,  # plain (unescaped) text
    host=host,
    port=port,
    database=database,
)
engine = create_engine(url_object)

def get_db():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def log_db(module, e):
    logging.error(f"Can not query on {module} Colection as Error: {e}")
    if os.path.isfile(f"logs/db/db_{module}.txt"):
        with open(f"logs/db/db_{module}.txt", "r", encoding="utf-8") as file:

            content = file.read()
    else: 
            content = ""
    date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    content += f"LOG AT {date_string}: Can not query on {module} Colection as Error: {e}"
    with open(f"logs/db/db_{module}.txt", "w", encoding="utf-8") as file:
        file.write(content)