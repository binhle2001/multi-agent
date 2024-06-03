import psycopg2
import random
from datetime import datetime, timedelta

# Thông tin kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="multi_agent",
    user="root",
    password="password",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Danh sách các loại vật liệu
materials = ["yên xe", "lốp xe", "vành xe", "ghi đông", "côn tay", "phanh xe", "ổ khóa"]

# Hàm tạo ngày ngẫu nhiên trong tháng 6
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

start_date = datetime.strptime("2024-06-01", "%Y-%m-%d")
end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")

# Tạo dữ liệu và chèn vào bảng
for material in materials:
    expired_date = random_date(start_date, end_date)
    quantity = random.randint(1000, 10000)
    cur.execute("""
        INSERT INTO chatbot_material (material_name, expired, quantity)
        VALUES (%s, %s, %s)
    """, (material, expired_date, quantity))

conn.commit()
cur.close()
conn.close()
