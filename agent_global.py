from fastapi import FastAPI, APIRouter, status
from fastapi.responses import JSONResponse
from helpers.global_catch_exception import catch_exceptions_middleware
import google.generativeai as genai
from helpers.common import get_datetime_now, get_env_var
import json
import logging
from pymongo import MongoClient
from datetime import datetime
import os
from helpers.gemini_config import *
from helpers.schema_api import *
from prompt.prompt_intent_classification import *
import uvicorn
import requests
from prompt.prompt_summarization import *
from apscheduler.schedulers.background import BackgroundScheduler
from agent_planing import get_produce_plan
from pytz import timezone
import pytz

os.makedirs("logs/planing", exist_ok=True)
os.makedirs("logs/communication", exist_ok=True)
os.makedirs("logs/db", exist_ok=True)
os.makedirs("logs/health", exist_ok=True)
os.environ["GEMINI_API_KEY"] = get_env_var("gemini", "GEMINI_API_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)


router = APIRouter(
    prefix = "/agent_global/api/v1",
    tags = ["Global"],
    dependencies = [],
    responses = {},
)

@router.get(
    "/ping"
)
async def ping():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "pong"})


@router.post(
    "/chat"
)
async def chat(query: Chat):
    prompt_intent = prompt_intent_classification.format(example_intent_1 = example_intent_1, example_intent_2 = example_intent_2, example_intent_3 = example_intent_3, example_intent_4 = example_intent_4, example_intent_5 = example_intent_5, example_intent_6 = example_intent_6, example_intent_7 = example_intent_7, example_intent_8 = example_intent_8, question = query.content)

    chat_session = model.start_chat(
            history=[
            ]
        )
    response = chat_session.send_message(prompt_intent)
    query_string = response.text.replace("```", "").replace("json", "").replace("\n", "")
    intent_json = json.loads(query_string)
    user = None
    machine = None
    material = None
    user_is_updated = None
    machine_is_updated = None
    material_is_updated = None
    if intent_json['hrm'] == ["READ"]:
        user = []
        response = requests.get(get_env_var("api_url", "HRM") + "/employee", json = {
            "content": query.content
        })
        if os.path.isfile("logs/communication/global_to_HRM.txt"):
            with open("logs/communication/global_to_HRM.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else: 
            content = ''
        date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content += "\n" + f"LOG AT {date_string}: GLOBAL: {query.content}"
        content += "\n" + f"LOG AT {date_string}: RESPONSE: {str(response.json())}"
        with open("logs/communication/global_to_HRM.txt", "w", encoding="utf-8") as file:
            file.write(content)

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            data = data["data"]
            if data is None:
                user = None
            else:
                for item in data:
                    user.append(item)

    if intent_json['hrm'] == ["UPDATE"]:
        user_is_updated = []
        response = requests.post(get_env_var("api_url", "HRM") + "/employee", json = {
            "content": query.content
        })
        if os.path.isfile("logs/communication/global_to_HRM.txt"):
            with open("logs/communication/global_to_HRM.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else: 
            content = ''
        date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content += "\n" + f"LOG AT {date_string}: GLOBAL: {query.content}"
        content += "\n" + f"LOG AT {date_string}: RESPONSE: {str(response.json())}"
        with open("logs/communication/global_to_HRM.txt", "w", encoding="utf-8") as file:
            file.write(content)

        get_produce_plan()
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            data = data["data_is_updated"]
            for item in data:
                user_is_updated.append(item)

    if intent_json["machine"] == ["READ"]:
        machine = []
        response = requests.get(get_env_var("api_url", "INVENTORY") + "/machine", json = {
            "content": query.content
        })
        if os.path.isfile("logs/communication/global_to_machine.txt"):
            with open("logs/communication/global_to_machine.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else: 
            content = ""
        
        date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content += "\n" + f"LOG AT {date_string}: GLOBAL: {query.content}"
        content += "\n" + f"LOG AT {date_string}: RESPONSE: {str(response.json())}"
        with open("logs/communication/global_to_machine.txt", "w", encoding="utf-8") as file:
            file.write(content)

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            data = data["data"]
            machine = data
    if intent_json["machine"] == ["UPDATE"]:
        machine_is_updated = []
        response = requests.post(get_env_var("api_url", "INVENTORY") + "/machine", json = {
            "content": query.content
        })
        if os.path.isfile("logs/communication/global_to_machine.txt"):
            with open("logs/communication/global_to_machine.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else: 
            content = ""
        
        date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content += "\n" + f"LOG AT {date_string}: GLOBAL: {query.content}"
        content += "\n" + f"LOG AT {date_string}: RESPONSE: {str(response.json())}"
        with open("logs/communication/global_to_machine.txt", "w", encoding="utf-8") as file:
            file.write(content)
        get_produce_plan()
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            data = data["data_is_updated"]
            for item in data:
                machine_is_updated.append(item)

    if intent_json["material"] == ["READ"]:
        material = []
        response = requests.get(get_env_var("api_url", "INVENTORY") + "/material", json = {
            "content": query.content
        })
        
        if os.path.isfile("logs/communication/global_to_material.txt"):
            with open("logs/communication/global_to_material.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else: 
            content = ""
        date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content += "\n" + f"LOG AT {date_string}: GLOBAL: {query.content}"
        content += "\n" + f"LOG AT {date_string}: RESPONSE: {str(response.json())}"
        with open("logs/communication/global_to_material.txt", "w", encoding="utf-8") as file:
            file.write(content)


        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            data = data["data"]
            for item in data:
                material.append(item)

    if intent_json["material"] == ["UPDATE"]:
        material_is_updated = []
        response = requests.post(get_env_var("api_url", "INVENTORY") + "/material", json = {
            "content": query.content
        })
        
        if os.path.isfile("logs/communication/global_to_material.txt"):
            with open("logs/communication/global_to_material.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else: 
            content = ""
        date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content += "\n" + f"LOG AT {date_string}: GLOBAL: {query.content}"
        content += "\n" + f"LOG AT {date_string}: RESPONSE: {str(response.json())}"
        with open("logs/communication/global_to_material.txt", "w", encoding="utf-8") as file:
            file.write(content)
        file.close()
        
        get_produce_plan()
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            data = data["data_is_updated"]
            for item in data:
                material_is_updated.append(item)
    data = {}
    if user is not None:
        data["user"] = user
    if machine is not None:
        data["machine"] = machine
    if material is not None:
        data["material"] = material
    if user_is_updated is not None:
        data["user_is_updated"] = user_is_updated
    if machine_is_updated is not None:
        data["machine_is_updated"] = machine_is_updated
    if material_is_updated is not None:
        data["material_is_updated"] = material_is_updated
    prompt_text = prompt_generation.format(question = query.content, json_data = str(data))
    # prompt_system = prompt_generation.format(json_data = str(data),)
    # openai_format = [{'role':'system', "content": prompt_system},{"role":"user", "content": query.content}]
    # output = llm.chat.completions.create(
    #                 model='gpt-3.5-turbo',
    #                 messages=openai_format,
    #                 temperature=0.1
    #             )
    # response_text =  output.choices[0].message.content
    chat_session = model.start_chat(
            history=[
            ]
        )
    output = chat_session.send_message(prompt_text)

    response = {
        "http_code": status.HTTP_200_OK,
        "message": output.text
        }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@router.get(
    "/planing"
)
async def get_plan():
    date_string = datetime.now().strftime("%d_%m_%Y")

    with open(f"planing/{date_string}.txt", "r", encoding="utf-8") as file:
        content = file.read()
    response = {
         "http_code": status.HTTP_200_OK,
         "planing": content
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@router.get("/shutdown")
def shutdown_event():
    scheduler.shutdown()


app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.middleware('http')(catch_exceptions_middleware)
app.include_router(router)


scheduler = BackgroundScheduler()
vietnam_tz = timezone('Asia/Ho_Chi_Minh')
# Schedule the function A() to run every day at 13
scheduler.add_job(get_produce_plan, 'cron', hour=14, minute=38, timezone=vietnam_tz)

# Start the scheduler
scheduler.start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8883)