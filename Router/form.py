from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.status import *
import os
from dotenv import load_dotenv
from fastapi import Request, Form
import requests
from Service.transaction_service import TransactionService
from sqlalchemy.orm import Session
import ast
import uuid
from Service.user_service import UserService

router = APIRouter(prefix="/form", tags=["form"])

load_dotenv(".env")
BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL")

templates = Jinja2Templates(directory="Templates")
@router.post("/create")
async def create_form(request: Request):
    try:
        data = await request.json()
        uid = data['userRequest']['user']['id']
        if UserService.get_user(uid) is None:
            UserService.save_user(UserService.to_user_entity(uid))
        form_id = str(uuid.uuid4())
        form_id = UserService.create_form(uid, form_id)
        url = BACKEND_SERVER_URL+"/form/submit/"+form_id
        json_form = {
            "version": "2.0",
            "template": {
                "outputs": [
                {
                    "basicCard": {
                    "title": "사용자 정보 입력",
                    "description": "간단한 본인의 정보를 입력해주세요",
                    "thumbnail": {
                        "imageUrl": "https://files.oaiusercontent.com/file-Pw29PPufbmCkto3ugOUb7Oua?se=2024-11-11T14%3A56%3A31Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3Df2e82db8-84d4-4596-ad10-8eaa8ce0f0c4.webp&sig=gDA42HqSQSTn7gRCIDJL/HHm5kysCkOYak1isil%2BhE0%3D"
                    },
                    "buttons": [
                        {
                        "action":  "webLink",
                        "label": "시작하기",
                        "webLinkUrl": url
                        }
                    ]
                    }
                }
                ]
            }
            }
        return JSONResponse(status_code=200, content=json_form)
    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": str(e)})
    
@router.get("/submit/{form_id}")
async def get_form(request: Request, form_id: str):
    try:
        if UserService.get_form(form_id):
            return templates.TemplateResponse("form.html", {"request": request, "form_id": form_id})
        return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"message": "만료된 폼입니다."})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})

@router.post("/submit/{form_id}")
async def submit_form(request: Request, form_id: str, name: str = Form(...), age: int = Form(...), gender: str = Form(...), disease: str = Form(None)):
    try:
        if uid := UserService.get_user_by_form_id(form_id):
            UserService.remove_form(form_id)
            UserService.save_user_info(uid, name, age, gender, disease)
        return JSONResponse(status_code=200, content={"message": "저장이 완료되었습니다."})
    except Exception as e:
        raise e
        return JSONResponse(status_code=500, content={"message": str(e)})