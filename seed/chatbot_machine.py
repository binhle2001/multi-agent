import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from faker import Faker

# Khởi tạo SQLAlchemy và Faker
Base = declarative_base()
fake = Faker()

# Định nghĩa mô hình chatbot_machine
class ChatbotMachine(Base):
    __tablename__ = 'chatbot_machine'
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_name = Column(String(30))
    expired = Column(DateTime)
    predicted = Column(DateTime)
    performance = Column(Integer)
    type = Column(String(30))

# Kết nối đến PostgreSQL
engine = create_engine('postgresql://root:password@localhost:5432/multi_agent')
Session = sessionmaker(bind=engine)
session = Session()

# Danh sách các loại máy
machine_types = ['máy cắt', 'máy mài', 'lò nung', 'máy rèn', 'máy check']

# Hàm tạo ngày random
def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

# Tạo dữ liệu và đổ vào bảng chatbot_machine
for i in range(1, 101):  # Tạo 100 bản ghi
    machine_type = random.choice(machine_types)
    machine_name = f'{machine_type}_{i}'
    expired = random_date(datetime(2024, 6, 1), datetime(2024, 6, 30))
    predicted = random_date(datetime(2024, 5, 15), datetime(2024, 6, 30))
    performance = random.randint(1000, 10000)
    
    machine = ChatbotMachine(
        machine_name=machine_name,
        expired=expired,
        predicted=predicted,
        performance=performance,
        type=machine_type
    )
    
    session.add(machine)

# Lưu thay đổi vào database
session.commit()
session.close()

print("Data inserted successfully!")
