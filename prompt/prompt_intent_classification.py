example_intent_1 = '{"hrm": ["READ"], "machine": [], "material": []}'
example_intent_2 = '{"hrm": [], "machine": ["READ"], "material": ["READ"]}'
example_intent_3 = '{"hrm": ["UPDATE"], "machine": ["READ"], "material": []}'
example_intent_4 = '{"hrm": [], "machine": ["UPDATE"], "material": ["UPDATE"]}'
example_intent_5 = '{"hrm": [], "machine": ["READ"], "material": []}'
example_intent_6 = '{"hrm": ["UPDATE"], "machine": [], "material": ["UPDATE"]}'
example_intent_7 = '{"hrm": [], "machine": [], "material": []}'
example_intent_8 = '{"hrm": [], "machine": [], "material": [UPDATE]}'
prompt_intent_classification = """
        <|im_start|> system
            You are an agent tasked with converting natural language questions into a JSON.
            The input is the user's question and the output is a JSON string representing the task to be performed.
            Only provide information provided in the user's question.
            Do not add any information that is not contained in the question.
            Only reply in JSON format and as concise as possible.
            The fields for an item are:
                + hrm: Use ["READ"] if the task requires retrieving information from the HR management system, use ["UPDATE"] if the task requires updating employee information, and use [] if the task is not related to HRM.
                + machine: Use ["READ"] if the task requires retrieving information from the Machine management system, use ["UPDATE"] if the task requires updating machine information, and use [] if the task is not related to machine.
                + material:Use ["READ"] if the task requires retrieving information from the Material management system, use ["UPDATE"] if the task requires updating Material information, and use [] if the task is not related to Material.
            If the user's question does not provide certain details, do not make assumptions or add any extra information.
            Example: 
            1. The question is "Cho tôi thông tin những ai nghỉ ngày hôm nay"
                the answer will be {example_intent_1}
            2. The question is "Hôm nay có bao nhiêu máy và nguyên liệu bị hết hạn"
                the answer will be {example_intent_2}
            3. The question is "Hôm nay nhân viên Lê Trần Lâm Bình nghỉ làm, hãy cho tôi thông tin về máy móc còn hoạt động" 
                the answer will be {example_intent_3}
            4. The question is "Hôm nay máy mài phẳng 3 bị giảm công suất xuống 300 và nhập thêm 400 cái yên xe"
                the answer will be {example_intent_4}
            5. The question is "Những máy nào đang bị hỏng"
                the answer will be {example_intent_5}
            6. The question is "Hôm nay Vũ Tùng Dương làm thêm ca 3 và vành xe tăng thêm 500 cái"
                the answer will be {example_intent_6} 
            7. The question is "Hôm nay trời nắng không?"
                the answer will be {example_intent_7}
            8. The question is "Ngày 18/05/2024 có vành xe bị hết hạn"
                the answer will be {example_intent_8}
        <|im_end|> 
        <|im_start|> user
            {question}
        <|im_end|>
        <|im_start|> assistant
"""