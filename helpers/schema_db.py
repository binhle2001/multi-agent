
from sqlalchemy import Column, Integer, String, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base

from .db_config import engine
from datetime import datetime

# Tạo engine và kết nối tới PostgreSQL

Base = declarative_base()

# Định nghĩa bảng trong PostgreSQL
class ChatbotWorkScheduler(Base):
    __tablename__ = 'chatbot_work_scheduler'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now())
    user_name = Column(String(30))
    working_time = Column(ARRAY(Integer), nullable=True, default=None)
    performance = Column(Integer, default=100)
    
class ChatbotMaterial(Base):
    __tablename__ = 'chatbot_material'
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_name = Column(String(30))
    expired = Column(DateTime)
    quantity = Column(Integer)

class ChatbotMachine(Base):
    __tablename__ = 'chatbot_machine'
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_name = Column(String(30))
    expired = Column(DateTime)
    predicted = Column(DateTime)
    performance = Column(Integer)
    type = Column(String(30))



# Tạo bảng nếu chưa tồn tại
Base.metadata.create_all(engine)

# Tạo session
