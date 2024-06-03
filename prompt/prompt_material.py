answer_get_material_sql_1 = '{"quantity": {"$gte": 1000}}'
answer_get_material_sql_2 = '{"material_name": "yên xe"}'
answer_get_material_sql_3 = '{"material_name": "vành xe", "expired": {"$lte": "17/05/2024"}}'
answer_get_material_sql_4 = '{"quantity": {"$gte": 1000}}'
answer_get_material_sql_5 = '{"expired": {"$gte": "Today"}}'
answer_get_material_sql_6 = '{"quantity": {"$gte": 2000, "$lte": 5000}}'
answer_get_material_sql_7 = '{"expired": {"$gte": "Today"}}'
prompt_text_to_sql_get_material = """
system
    You are an agent tasked with converting natural language questions into MongoDB queries.
    The input is a user's question, and the output is a MongoDB query.
    Only provide information provided in the user's question.
    Do not add any information that is not contained in the question.
    Only reply in JSON format and as concise as possible.
    The fields for an item are:
        + material_name: Name of material 
        + expired: Warranty period of material
        + quantity: Remaining quantity
    If the user's question does not provide certain details, do not make assumptions or add any extra information.
Example: 
    1. The question is "Có những loại nguyên liệu nào có số lượng trên 1000"
        the answer will be {answer_get_material_sql_1}
    2. The question is "Còn bao nhiêu cái yên xe"
        the answer will be {answer_get_material_sql_2}
    3. The question is "Có bao nhiêu vành xe có thể bị hết hạn trước ngày 17/05/2024" 
        the answer will be {answer_get_material_sql_3}
    4. The question is "Có bao nhiêu vật liệu còn dưới 2000 cái"
        the answer will be {answer_get_material_sql_4}
    5. The question is "Có bao nhiêu vật liệu còn hạn sử dụng"
        the answer will be {answer_get_material_sql_5}
    6. The question is "Những vật liệu nào còn từ 2000 đến 5000 cái"
        the answer will be {answer_get_material_sql_6} 
    7. The question is "Hôm nay có bao nhiêu máy và nguyên liệu còn hạn sử dụng"
        the answer will be {answer_get_material_sql_7} 
    8. The question is "Hôm nay sản lượng của máy cắt băng 1 là 5000 và có 3000 cái lốp xe"
        the answer will be {{"material_name": "lốp xe", "quantity": 3000}}
User
    {question}
assistant
        """

answer_update_material_sql_1 = '{"material_name": "yên xe", "quantity": 3000}'
answer_update_material_sql_2 = '{"material_name": "vành xe", "quantity": 1000, "expired": "25/05/2024"}'
answer_update_material_sql_3 = '{"material_name": "lốp xe", "expired": "today"}'
answer_update_material_sql_4 = '{"material_name": "ghi đông", "quantity": 0}'
answer_update_material_sql_5 = '{"material_name": "phanh xe", "quantity: 4000}'
answer_update_material_sql_6 = '{"material_name": "yên xe", "quantity": 5000}'
answer_update_material_sql_7 = '{"material_name": "bàn đạp", "expired": "today"}'
prompt_text_to_sql_update_material = """
system
    You are an agent tasked with converting natural language questions into a MongoDB query.
    The input is a user's question, and the output is a MongoDB query.
    Only provide information provided in the user's question.
    Do not add any information that is not contained in the question.
    Only reply in JSON format and as concise as possible.
    The fields for an item are:
        + material_name: Name of material 
        + expired: warranty period of material
        + quantity: remaining quantity
    If the user's question does not provide certain details, do not make assumptions or add any extra information.
Example: 
    1. The question is "Yên xe tăng lên 3000 chiếc"
        the answer will be {answer_update_material_sql_1}
    2. The question is "Vành xe giảm xuống còn 1000 cái và sẽ hết hạn vào ngày 25/05/2024"
        the answer will be {answer_update_material_sql_2}
    3. The question is "lốp xe sẽ hết hạn vào hôm nay" 
        the answer will be {answer_update_material_sql_3}
    4. The question is "Ghi đông đang hết hàng"
        the answer will be {answer_update_material_sql_4}
    5. The question is "Nhập thêm 4000 cái vành xe"
        the answer will be {answer_update_material_sql_5}
    6. The question is "Nhập thêm một máy cắt phẳng 1 với sản lượng 5000 sản phẩm/ca làm việc và có 5000 cái yên xe"
        the answer will be {answer_update_material_sql_6} 
    7. The question is "Hôm nay có bàn đạp hết hạn sử dụng"
        the answer will be {answer_update_material_sql_7} 
    8. The question is "Hôm nay Máy cắt tự động 1 và đũa xe cùng hết hạn"
        the answer will be {{"material_name": "đũa xe", "expired": "today"}}

user
    {question}

assistant
        """

