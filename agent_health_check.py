import requests
from fastapi import status, APIRouter, FastAPI
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
from helpers.common import get_env_var
from helpers.global_catch_exception import catch_exceptions_middleware

router = APIRouter(
    prefix = "/agent_health_check/api/v1",
    tags = ["Health_Check"],
    dependencies = [],
    responses = {},
)

def health_check_active():
    response = requests.get(get_env_var("api_url", "INVENTORY") + "/ping")
    date_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if response.status_code != status.HTTP_200_OK:
        if os.path.isfile("logs/health/inventory_health.txt"):
            with open("logs/health/inventory_health.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else:
            content = ""
        content += "\n" + f"LOG AT {date_string}: AGENT_INVENTORY not working"
        with open("logs/health/inventory_health.txt", "w", encoding="utf-8") as file:
            file.write(content)

    response = requests.get(get_env_var("api_url", "HRM") + "/ping")
    if response.status_code != status.HTTP_200_OK:

        if os.path.isfile("logs/health/hrm_health.txt"):
            with open("logs/health/hrm_health.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else:
            content = ""
        content += "\n" + f"LOG AT {date_string}: AGENT_HRM not working"
        with open("logs/health/hrm_health.txt", "r", encoding="utf-8") as file:
            file.write(content)


    response = requests.get(get_env_var("api_url", "GLOBAL") + "/ping")
    if response.status_code != status.HTTP_200_OK:
        if os.path.isfile("logs/health/global_health.txt"):
            with open("logs/health/global_health.txt", "r", encoding="utf-8") as file:
                content = file.read()
        else:
            content = ""
        content += "\n" + f"LOG AT {date_string}: AGENT_GLOBAL not working"
        with open("logs/health/global_health.txt", "w", encoding="utf-8") as file:
            file.write(content)

@router.get(
    "/communication"
)
async def get_community():
    data = {}
    for item in os.listdir("logs/communication"):
        file_path = "logs/communication/" + item
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        data[item[:-4]] = content

    response = {
        "http_code": status.HTTP_200_OK,
        "data": data
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content= response)

@router.get(
    "/health_check"
)
async def get_health_check():
    data = []
    for item in os.listdir("logs/health"):
        with open(f"logs/health/{item}", "r", encoding="utf-8") as file:
            content = file.read()
        data["item"] = content
    response = {
        "http_code": status.HTTP_200_OK,
        "data": data
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

@router.get(
    "/db"
)
async def get_health_check():
    data = {}
    for item in os.listdir("logs/db"):
        with open(f"logs/db/{item}", "r", encoding="utf-8") as file:
            content = file.read()
        data[item[:-4]] = content
    response = {
        "http_code": status.HTTP_200_OK,
        "data": data
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)



# Tạo một instance của APScheduler
scheduler = BackgroundScheduler()

# Thêm cron job để gọi hàm health_check mỗi 5 giây
scheduler.add_job(health_check_active, 'interval', seconds=5)

# Bắt đầu scheduler
scheduler.start()

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
    uvicorn.run(app, host="0.0.0.0", port=8884)
        


    