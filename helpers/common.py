from configparser import ConfigParser
import os
from datetime import datetime, date

def get_env_var(group, var_name): 
    config = ConfigParser()
    file_path = ".env"
    if os.path.isfile(file_path):
        config.read(file_path)
        return config[group][var_name]
    return os.environ.get(var_name)

def get_datetime_now():
    today = datetime.now()

    # Thiết lập thời gian bắt đầu vào lúc bắt đầu ngày hôm nay (00:00:00)
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Thiết lập thời gian kết thúc vào trước khi kết thúc ngày hôm nay (23:59:59.999999)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Cập nhật truy vấn để tìm các tài liệu trong khoảng thời gian này
    return {
        '$gte': start_of_today,
        '$lte': end_of_today
    }


def is_subarray(arr, sub_arr):
    if sub_arr == []:
        if arr != []:
            return False
        return True
    # Chuyển đổi mảng thành chuỗi để sử dụng phương thức find
    arr_str = ' '.join(map(str, arr))
    sub_arr_str = ' '.join(map(str, sub_arr))
    
    # Kiểm tra nếu chuỗi sub_arr là một phần của chuỗi arr
    return arr_str.find(sub_arr_str) != -1

