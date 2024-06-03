from fastapi import FastAPI, APIRouter, status
from fastapi.responses import JSONResponse
from helpers.global_catch_exception import catch_exceptions_middleware
from helpers.schema_db import ChatbotWorkScheduler
from helpers.common import is_subarray
from prompt.prompt_hrm import *
import google.generativeai as genai
from helpers.gemini_config import *
import uvicorn
from helpers.schema_api import *
import os
from helpers.common import get_datetime_now, get_env_var
import json
import logging
from pymongo import MongoClient
from datetime import datetime
from helpers.db_config import get_db, log_db
from sqlalchemy import func


os.environ["GEMINI_API_KEY"] = get_env_var("gemini", "GEMINI_API_KEY")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)


router = APIRouter(
    prefix = "/agent_hrm/api/v1",
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
    "/employee"
)
async def get_info(query: Query_HRM):
    session = get_db()
    prompt_text = prompt_text_to_sql_get_hrm.format(answer_hrm_sql_get_1 = answer_hrm_sql_get_1, answer_hrm_sql_get_2 = answer_hrm_sql_get_2, answer_hrm_sql_get_3 = answer_hrm_sql_get_3, answer_hrm_sql_get_4 = answer_hrm_sql_get_4, answer_hrm_sql_get_5 = answer_hrm_sql_get_5, answer_hrm_sql_get_6 = answer_hrm_sql_get_6, answer_hrm_sql_get_7 = answer_hrm_sql_get_7, answer_hrm_sql_get_8 = answer_hrm_sql_get_8, answer_hrm_sql_get_9 = answer_hrm_sql_get_9, question = query.content)
    chat_session = model.start_chat(
        history=[
        ]
    )
    response = chat_session.send_message(prompt_text)
    query_string = response.text.replace("```", "").replace("json", "")
    json_query = json.loads(query_string)
    if json_query["date"].lower() == "today":
        json_query["date"] = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        json_query["date"] = datetime.strptime(json_query["date"], "%d/%m/%Y")

    if json_query["date"] > datetime.now():
        json_response = {
        "http_code": status.HTTP_200_OK,
        "data": None
    }
        return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)
    data = []
    performance_min = 0
    performance_max = 999999999999999
    print(json_query)
    if "performance" in json_query:
        performance = json_query["performance"]
        if "$gte" in performance:
            performance_min = performance["$gte"]
        if "$lte" in performance:
            performance_max = performance["$lte"]
        del json_query["performance"]
    
    if "working_time" in json_query and isinstance(json_query["working_time"], list):
        try:
            working_times = json_query["working_time"]
            del json_query["working_time"]
            
            results_list = session.query(ChatbotWorkScheduler).filter_by(**json_query).all()
            for document in results_list:
                if document.performance <= performance_max and document.performance >= performance_min and is_subarray(document.working_time, working_times):
                    item = {
                            "user_name": document.user_name,
                            "date": document.date.strftime("%d/%m/%Y"),
                            "working_time": document.working_time,
                            "performance": document.performance
                        }
                    data.append(item)
        except Exception as e:
            log_db("hrm", e)

    elif "working_time" in json_query and isinstance(json_query["working_time"], dict):
        try:
            del json_query["working_time"]
            results_list = session.query(ChatbotWorkScheduler).filter_by(**json_query)
            results_list = results_list.filter(func.array_length(ChatbotWorkScheduler.working_time, 1) > 0).all()
            for document in results_list:
                    if document.performance <= performance_max and document.performance >= performance_min:
                        item = {
                            "user_name": document.user_name,
                            "date": document.date.strftime("%d/%m/%Y"),
                            "working_time": document.working_time,
                            "performance": document.performance
                        }
                        data.append(item)
        except Exception as e:
            log_db("hrm", e)
    else:
        try:
            
            results_list = session.query(ChatbotWorkScheduler).filter_by(**json_query).all()
            for document in results_list:
                if document.performance <= performance_max and document.performance >= performance_min:
                    item = {
                            "user_name": document.user_name,
                            "date": document.date.strftime("%d/%m/%Y"),
                            "working_time": document.working_time,
                            "performance": document.performance
                        }
                    data.append(item)
        except Exception as e:
            log_db("hrm", e)    
    json_response = {
        "http_code": status.HTTP_200_OK,
        "data": data
    }
    session.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)

@router.post(
    "/employee"
)
async def get_info(query: Query_HRM):
    session = get_db()
    prompt_text = prompt_text_to_sql_post_hrm.format(answer_hrm_sql_post_1 = answer_hrm_sql_post_1, answer_hrm_sql_post_2 = answer_hrm_sql_post_2, answer_hrm_sql_post_3 = answer_hrm_sql_post_3, answer_hrm_sql_post_4 = answer_hrm_sql_post_4, answer_hrm_sql_post_5 = answer_hrm_sql_post_5, answer_hrm_sql_post_6 = answer_hrm_sql_post_6, answer_hrm_sql_post_7 = answer_hrm_sql_post_7, answer_hrm_sql_post_8 = answer_hrm_sql_post_8, question = query.content)
    chat_session = model.start_chat(
        history=[
        ]
    )
    response = chat_session.send_message(prompt_text)
    query_string = response.text.replace("```", "").replace("json", "")
    
    json_query = json.loads(query_string)
    print(json_query)
    if json_query["date"].lower() == "today":
        json_query["date"] = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        json_query["date"] = datetime.strptime(json_query["date"], "%d/%m/%Y")
    try:
        if "user_name" in json_query:
            item_query =  {
                "user_name": json_query["user_name"],
                "date": json_query["date"]
            }
        else:
            item_query =  {
                "date": json_query["date"]
            }
        results_list = session.query(ChatbotWorkScheduler).filter_by(**item_query).all()
        session.query(ChatbotWorkScheduler).filter_by(**item_query).delete()
    except Exception as e:
        log_db("hrm", e)
    data = []
    for document in results_list:
        document = document.__dict__
        item = json_query
        item["date"] = document["date"]
        for key in document.keys():
            if key not in json_query:
                item[key] = document[key]
        data.append(item)
    if len(data) == 0:
        if "performance" not in json_query:
            json_query["performance"] = 100
        if "working_time" not in json_query:
            json_query["working_time"] = [1]
        data.append(json_query)
    
    for item in data: 
        new_record = ChatbotWorkScheduler(
            user_name = item["user_name"],
            date = item["date"],
            performance = item["performance"],
            working_time = item["working_time"]
        )
        session.add(new_record)
    results_list = session.query(ChatbotWorkScheduler).filter_by(**item_query).all()
    data = []
    for document in results_list:
        item = {
            "user_name": document.user_name,
            "date": document.date.strftime("%d/%m/%Y"),
            "working_time": document.working_time,
            "performance": document.performance
        }
        data.append(item)
    json_response = {
        "http_code": status.HTTP_200_OK,
        "data_is_updated": data
    }
    print(data)
    session.commit()
    session.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content=json_response)



@router.get(
    "/daily_report"
)
async def daily_report():
    session = get_db()
    query_employee = {
        "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
    }
    try: 
        data = session.query(ChatbotWorkScheduler).filter_by(**query_employee).all()
    except Exception as e:
        log_db("hrm", e)

    absents = []
    workers = []
    for employee in data:
        item = {
            "user_name": employee.user_name,
            "date": employee.date.strftime("%d/%m/%Y"),
            "working_time": employee.working_time,
            "performance": employee.performance
        }
        if len(employee.working_time) != 0:
            workers.append(item)
        else:
            absents.append(item)
    session.close()
    response = {
        "http_code": status.HTTP_200_OK,
        "workers": workers,
        "absents": absents
    }
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
    uvicorn.run(app, host="0.0.0.0", port= 8882)