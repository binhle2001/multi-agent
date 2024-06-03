import psycopg2
from psycopg2 import sql
from faker import Faker
import random
from datetime import datetime, timedelta

# Kết nối đến cơ sở dữ liệu PostgreSQL
conn = psycopg2.connect(
    dbname="multi_agent",
    user="root",
    password="password",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Tạo đối tượng Faker để tạo dữ liệu giả
fake = Faker('vi_VN')

# Hàm tạo danh sách các ngày từ 1/6 đến 10/6
def generate_dates(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)

# Định nghĩa khoảng thời gian và khoảng performance
start_date = datetime(2024, 6, 1)
end_date = datetime(2024, 6, 10)
performance_range = (50, 300)

# Tạo dữ liệu và chèn vào bảng
for date in generate_dates(start_date, end_date):
    for _ in range(random.randint(5, 10)):  # Giả lập số lượng bản ghi mỗi ngày
        user_name = fake.name()
        working_time = random.choices([[], [1], [2], [3], [1, 2], [2, 3], [1, 3], [1, 2, 3]], k=1)[0]
        performance = random.randint(*performance_range)
        
        cursor.execute(
            sql.SQL("INSERT INTO chatbot_work_scheduler (date, user_name, working_time, performance) VALUES (%s, %s, %s, %s)"),
            [date, user_name, working_time, performance]
        )

# Lưu thay đổi và đóng kết nối
conn.commit()
cursor.close()
conn.close()
