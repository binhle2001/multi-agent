from fastapi import FastAPI, APIRouter, status
from fastapi.responses import JSONResponse
from helpers.global_catch_exception import catch_exceptions_middleware
from prompt.prompt_machine import *
from prompt.prompt_material import *
import google.generativeai as genai
from helpers.gemini_config import *
import uvicorn
from helpers.schema_api import *
import os
from helpers.common import get_datetime_now, get_env_var
import json
import logging
from datetime import datetime
from helpers.db_config import get_db, log_db
from helpers.schema_db import ChatbotMachine, ChatbotMaterial



os.environ["GEMINI_API_KEY"] = get_env_var("gemini", "GEMINI_API_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)


router = APIRouter(
    prefix = "/agent_inventory/api/v1",
    tags = ["HRM"],
    dependencies = [],
    responses = {},
)


@router.get(
    "/ping"
)
async def ping():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "pong"})



@router.get(
    "/machine"
)
async def get_info_machine(query: QueryMachine):
    session = get_db()
    prompt_text = prompt_text_to_sql_get_machine.format(question = query.content)
    chat_session = model.start_chat(
        history=[
        ]
    )
    response = chat_session.send_message(prompt_text)
    query_string = response.text.replace("```", "").replace("json", "")
    print(query_string)
    json_query = json.loads(query_string)
    performance_max = 9999999999
    performance_min = -1
    if "performance" in json_query:
        if "$gte" in json_query["performance"]:
            performance_min = json_query["performance"]["$gte"]
        if "$gt" in json_query["performance"]:
            performance_min = json_query["performance"]["$gt"]
        if "$lte" in json_query["performance"]:
            performance_max = json_query["performance"]["$lte"]
        if "$lt" in json_query["performance"]:
            performance_max = json_query["performance"]["$lt"]
        del json_query["performance"]
    
    expired_max = datetime.strptime("1/1/2099", "%d/%m/%Y")
    expired_min = datetime.strptime("1/1/1099", "%d/%m/%Y")
    if "expired" in json_query:
        if "$gte" in json_query["expired"]:
            if json_query["expired"]["$gte"].lower() == "today":
                expired_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_min = datetime.strptime(json_query["expired"]["$gte"], "%d/%m/%Y")
        if "$gt" in json_query["expired"]:
            if json_query["expired"]["$gt"].lower() == "today":
                expired_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_min = datetime.strptime(json_query["expired"]["$gt"], "%d/%m/%Y")
        if "$lte" in json_query["expired"]:
            if json_query["expired"]["$lte"].lower() == "today":
                expired_max = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_max = datetime.strptime(json_query["expired"]["$lte"], "%d/%m/%Y")
        if "$lt" in json_query["expired"]:
            if json_query["expired"]["$lt"].lower() == "today":
                expired_max = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_max = datetime.strptime(json_query["expired"]["$lt"], "%d/%m/%Y")
        del json_query["expired"]
    predicted_max = datetime.strptime("1/1/2099", "%d/%m/%Y")
    predicted_min = datetime.strptime("1/1/1099", "%d/%m/%Y")
    if "predicted" in json_query:
        if "$gte" in json_query["predicted"]:
            if json_query["predicted"]["$gte"].lower() == "today":
                predicted_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                predicted_min = datetime.strptime(json_query["predicted"]["$gte"], "%d/%m/%Y")
        if "$lte" in json_query["predicted"]:
            if json_query["predicted"]["$lte"].lower() == "today":
                predicted_max = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                predicted_max = datetime.strptime(json_query["predicted"]["$lte"], "%d/%m/%Y")
        del json_query["predicted"]
    try:
        results_list = session.query(ChatbotMachine).filter_by(**json_query).all()
    except Exception as e:
        log_db("machine", e)

    broken = []
    expired = []
    working = []
    for document in results_list:
        if (document.expired <= expired_max and
            document.expired >= expired_min and
            document.predicted <= predicted_max and
            document.predicted >= predicted_min and
            document.performance >= performance_min and
            document.performance <= performance_max):
            item = {
                "machine_name": document.machine_name,
                "expired": document.expired.strftime("%d/%m/%Y"),
                "predicted": document.predicted.strftime("%d/%m/%Y"),
                "performance": document.performance,
                "type_of_machine": document.type,
        }
            if document.expired < datetime.now():
                expired.append(item)
            elif document.predicted < datetime.now():
                broken.append(item)
            else:
                working.append(item)
    data = {}
    if broken != []:
        data["broken_down"] = broken
    if expired != []:
        data["expired"] = expired
    if working != []:
        data["working"] = working
    json_response = {
        "http_code": status.HTTP_200_OK,
        "data": data
    }
    session.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)

@router.post(
    "/machine"
)
async def update_info_machine(query: QueryMachine):
    prompt_text = prompt_text_to_sql_update_machine.format( question = query.content)
    chat_session = model.start_chat(
        history=[
        ]
    )
    session = get_db()
    response = chat_session.send_message(prompt_text)
    query_string = response.text.replace("```", "").replace("json", "")

    json_query = json.loads(query_string)
    if "expired" in json_query:
            date = json_query["expired"]
            if date.lower() == "today":
                date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                date = datetime.strptime(date, "%d/%m/%Y")
            json_query["expired"] = date
            
    
    if "predicted" in json_query:
            date = json_query["predicted"]
            if date.lower() == "today":
                date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                date = datetime.strptime(date, "%d/%m/%Y")
            json_query["predicted"] = date
    item_query = {
            "machine_name": json_query["machine_name"]
        }
    try:
        
        results_list = session.query(ChatbotMachine).filter_by(**item_query).all()
        session.query(ChatbotMachine).filter_by(**item_query).delete()
    except Exception as e:
        log_db("machine", e)

    data = []
    for document in results_list:
        item = json_query
        document = document.__dict__
        for key in document.keys():
            if key not in json_query:
                item[key] = document[key]
        data.append(item)
    if len(data) == 0:
        if "expired" not in json_query:
            json_query["expired"] = datetime.strptime("22/12/2099", "%d/%m/%Y")
        if "predicted" not in json_query:
            json_query["predicted"] = datetime.strptime("22/12/2099", "%d/%m/%Y")
        if "performance" not in json_query:
            json_query["performance"] = 2000
        data = [json_query]
    for item in data:
        new_record = ChatbotMachine(
            machine_name = item["machine_name"],
            expired = item["expired"],
            predicted = item["predicted"],
            performance = item["performance"],
            type = item["type"]
        )
        session.add(new_record)

    results_list = session.query(ChatbotMachine).filter_by(**item_query).all()
    data = []
    for document in results_list:
        item = {
            "machine_name": document.machine_name,
            "expired": document.expired.strftime("%d/%m/%Y"),
            "predicted": document.predicted.strftime("%d/%m/%Y"),
            "performance": document.performance,
            "type_of_machine": document.type,
        }
        data.append(item)
    session.commit()
    session.close()
    json_response = {
        "http_code": status.HTTP_200_OK,
        "data_is_updated": data
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)



@router.get(
    "/material"
)
async def get_info(query: QueryMaterial):
    session = get_db()
    prompt_text = prompt_text_to_sql_get_material.format(answer_get_material_sql_1 = answer_get_material_sql_1, answer_get_material_sql_2 = answer_get_material_sql_2, answer_get_material_sql_3 = answer_get_material_sql_3, answer_get_material_sql_4 = answer_get_material_sql_4, answer_get_material_sql_5 = answer_get_material_sql_5, answer_get_material_sql_6 = answer_get_material_sql_6,answer_get_material_sql_7 = answer_get_material_sql_7, question = query.content)
    chat_session = model.start_chat(
        history=[
        ]
    )
    response = chat_session.send_message(prompt_text)
    query_string = response.text.replace("```", "").replace("json", "")

    json_query = json.loads(query_string)
    expired_max = datetime.strptime("1/1/2099", "%d/%m/%Y")
    expired_min = datetime.strptime("1/1/1099", "%d/%m/%Y")
    quantity_max = 9999999999
    quantity_min = -1
    print(json_query)
    if "quantity" in json_query:
        if "$gte" in json_query["quantity"]:
            quantity_min = json_query["quantity"]["$gte"]
        if "$lte" in json_query["quantity"]:
            quantity_max = json_query["quantity"]["$lte"]
        if "$gt" in json_query["quantity"]:
            quantity_min = json_query["quantity"]["$gt"]
        if "$lt" in json_query["quantity"]:
            quantity_max = json_query["quantity"]["$lt"]
        del json_query["quantity"]
    if "expired" in json_query:
        if "$gte" in json_query["expired"]:
            if json_query["expired"]["$gte"].lower() == "today":
                expired_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_min = datetime.strptime(json_query["expired"]["$gte"], "%d/%m/%Y")
        if "$lte" in json_query["expired"]:
            if json_query["expired"]["$lte"].lower() == "today":
                expired_max = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_max = datetime.strptime(json_query["expired"]["$lte"], "%d/%m/%Y")
        if "$gt" in json_query["expired"]:
            if json_query["expired"]["$gt"].lower() == "today":
                expired_min = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_min = datetime.strptime(json_query["expired"]["$gt"], "%d/%m/%Y")
        if "$lt" in json_query["expired"]:
            if json_query["expired"]["$lt"].lower() == "today":
                expired_max = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else: 
                expired_max = datetime.strptime(json_query["expired"]["$lt"], "%d/%m/%Y")
        del json_query["expired"]
    try:
        results_list = session.query(ChatbotMaterial).filter_by(**json_query).all()
    except Exception as e:
        log_db("material", e)

    expired = []
    in_use = []
    data = {}
    for document in results_list:
        if document.expired >= expired_min and document.expired <= expired_max and document.quantity >= quantity_min and document.quantity <= quantity_max:
            item = {
                "material_name": document.material_name,
                "expired": document.expired.strftime("%d/%m/%Y"),
                "quantity": document.quantity,
            }
            if document.expired < datetime.now():
                expired.append(item)
            else:
                in_use.append(item)
    if len(expired) != 0:
        data["expired"] = expired
    if len(in_use) != 0:
        data["in_use"] = in_use
    session.close()
    json_response = {
        "http_code": status.HTTP_200_OK,
        "data": data
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)

@router.post(
    "/material"
)
async def update_info(query: QueryMaterial):
    session = get_db()
    prompt_text = prompt_text_to_sql_update_material.format(answer_update_material_sql_1 = answer_update_material_sql_1, answer_update_material_sql_2 = answer_update_material_sql_2, answer_update_material_sql_3 = answer_update_material_sql_3, answer_update_material_sql_4 = answer_update_material_sql_4, answer_update_material_sql_5 = answer_update_material_sql_5, answer_update_material_sql_6 = answer_update_material_sql_6,answer_update_material_sql_7 = answer_update_material_sql_7, question = query.content)
    chat_session = model.start_chat(
        history=[
        ]
    )
    response = chat_session.send_message(prompt_text)
    query_string = response.text.replace("```", "").replace("json", "")
    print(query_string)
    json_query = json.loads(query_string)
    if "expired" in json_query:
        date = json_query["expired"]
        if date.lower() == "today":
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            date = datetime.strptime(date, "%d/%m/%Y")
        json_query["expired"] = date
    item_query = {
        "material_name": json_query["material_name"]
    }
    try:
        results_list = session.query(ChatbotMaterial).filter_by(**item_query).all()
        session.query(ChatbotMaterial).filter_by(**item_query).delete()
    except Exception as e:
        log_db("material", e)
    
    data = []
    for document in results_list:
        item = json_query
        document = document.__dict__
        for key in document.keys():
            if key not in json_query:
                item[key] = document[key]
        data.append(item)
    if len(data) == 0:
        if "expired" not in json_query:
            json_query["expired"] = datetime.strptime("22/12/2099", "%d/%m/%Y")
        if "quantity" not in json_query:
            json_query["quantity"] = 3000
        data = [json_query]
    
    
    for item in data:
        new_record = ChatbotMaterial(
            material_name = item["material_name"],
            expired = item["expired"],
            quantity =  item["quantity"]
        )
        session.add(new_record)
    results_list = session.query(ChatbotMaterial).all()

    data = []
    for document in results_list:
        item = {
            "material_name": document.material_name,
            "expired": document.expired.strftime("%d/%m/%Y"),
            "quantity": document.quantity,
        }
        data.append(item)
    session.commit()
    session.close()
    json_response = {
        "http_code": status.HTTP_200_OK,
        "data_is_updated": data
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)



@router.get(
    "/daily_report_machine"
)
async def daily_report():
    session = get_db()
    try:
        data = session.query(ChatbotMachine).all()
    except Exception as e:
        log_db("machine", e)

    expired = []
    broken = []
    working = []
    for document in data:

        item = {
            "machine_name": document.machine_name,
            "expired": document.expired.strftime("%d/%m/%Y"),
            "predicted": document.predicted.strftime("%d/%m/%Y"),
            "performance": document.performance,
            "type_of_machine": document.type,
        }
        if document.expired < datetime.now():
            expired.append(item)
        if document.predicted < datetime.now():
            broken.append(item)
        if document.expired > datetime.now() and document.predicted < datetime.now():
            working.append(item)


    session.close()
    response = {
        "http_code": status.HTTP_200_OK,
        "expired": expired,
        "broken": broken,
        "working": working
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@router.get(
    "/daily_report_material"
)
async def daily_report():
    session = get_db()
    try:
        data = session.query(ChatbotMaterial).all()
    except Exception as e:
        log_db("material", e)
    expired = []
    in_used = []
    
    for material in data:
        item = {
            "material_name": material.material_name,
            "expired": material.expired.strftime("%d/%m/%Y"),
            "quantity": material.quantity,
        }
        if material.expired < datetime.now():
            expired.append(item)
        else:
            in_used.append(item)
    response = {
        "http_code": status.HTTP_200_OK,
        "expired": expired,
        "in_used": in_used
    }
    session.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port= 8881)