from datetime import datetime
import requests
import json
from prompt.prompt_planing import *
import google.generativeai as genai
import os
from helpers.common import get_env_var
from helpers.gemini_config import *

os.environ["GEMINI_API_KEY"] = get_env_var("gemini", "GEMINI_API_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

def get_data(url):
    res = requests.get(url)
    res = json.loads(res.text)
    return res

# Quy định công đoạn sản xuất
stages = {
    "Lắp ráp yên xe và khung xe": ["yên xe", "khung xe"],
    "Lắp dây phanh và má phanh": ["dây phanh", "má phanh"]
}
# Hàm tính toán năng suất của nhân viên
def calculate_workers_performance(workers, date: str):
    worker_performances = {}
    for worker in workers:
        if worker["date"] == date:
            worker_performances[worker["user_name"]] = len(worker["working_time"]) * worker["performance"]
    return worker_performances
# Hàm tính toán năng suất của máy móc
def calculate_machines_performance(machines, date):
    machine_performances = {}
    for machine in machines:
        if datetime.strptime(machine["predicted"], "%d/%m/%Y")<= datetime.strptime(date, "%d/%m/%Y"):
            machine_performances[machine["machine_name"]] = machine["performance"]
    return machine_performances
# Hàm kiểm tra và cập nhật số lượng nguyên liệu
def update_materials_usage(in_used, used_materials):
    for material_name, quantity_used in used_materials.items():
        for material in in_used:
            if material["material_name"] == material_name:
                material["quantity"] -= quantity_used
                if material["quantity"] < 0:
                    return False, material_name
    return True, None
# Lập kế hoạch sản xuất
def production_plan(workers: list, working: list, in_used: list, stages, date:str):
    worker_performances = calculate_workers_performance(workers, date)
    machine_performances = calculate_machines_performance(working, date)
    total_performance = sum(worker_performances.values()) + sum(machine_performances.values())
    # Giả sử mỗi công đoạn cần 1 máy và 1 công nhân
    plan_details = []
    used_materials = {}
    worker_index = 0
    for stage, materials in stages.items():
        if worker_index >= len(worker_performances):
            break
        worker_name = list(worker_performances.keys())[worker_index]
        # machine_name = list(machine_performances.keys())[worker_index]
        plan_details.append({
            "stage": stage,
            "worker": worker_name,
            # "machine": machine_name,
            "materials_used": materials
        })
        for material in materials:
            if material in used_materials:
                used_materials[material] += 1
            else:
                used_materials[material] = 1
        worker_index += 1
    materials_available, material_name = update_materials_usage(in_used, used_materials)
    if not materials_available:
        return json.dumps({
            "date": date,
            "total_performance": total_performance,
            "plan_details": plan_details,
            "materials_status": f"Không đủ nguyên liệu: {material_name}",
            "remaining_materials": in_used
        }, ensure_ascii=False, indent=4)
    return json.dumps({
        "date": date,
        "total_performance": total_performance,
        "plan_details": plan_details,
        "materials_status": "Đủ nguyên liệu",
        "remaining_materials": in_used
    }, ensure_ascii=False, indent=4)



def get_produce_plan():
    data_worker = get_data("http://192.168.0.248:8882/agent_hrm/api/v1/daily_report")["workers"]
    data_machine = get_data("http://192.168.0.248:8881/agent_inventory/api/v1/daily_report_machine")["working"]
    data_material = get_data("http://192.168.0.248:8881/agent_inventory/api/v1/daily_report_material")["in_used"]
    # Ngày cần lập kế hoạch sản xuất
    date = datetime.now().strftime("%d/%m/%Y")
    # Lập kế hoạch sản xuất
    plan = production_plan(data_worker, data_machine, data_material, stages, date)
    chat_session = model.start_chat(
            history=[
            ]
        )
    output = chat_session.send_message(prompt_summarize_data_report.format(plan=plan))
    date_string = datetime.now().strftime("%d_%m_%Y")
    with open(f"planing/{date_string}.txt", "w", encoding="utf-8") as file:
        file.write(output.text)
    

