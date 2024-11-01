from fastapi.responses import JSONResponse
from Database.database import get_db, rollback_to_savepoint
from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.status import *
import os
from Data.chat import QuestionData, AnswerData
from dotenv import load_dotenv
from fastapi import Request
import requests
from Service.transaction_service import TransactionService
from sqlalchemy.orm import Session
import ast


router = APIRouter(prefix="/api")
load_dotenv(".env")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")
FRONTEND_SERVER_URL = os.getenv("FRONTEND_SERVER_URL")

@router.post("/ask", tags=["ask"])
async def ask(request: Request, question: QuestionData, background_tasks: BackgroundTasks):
    try:
        # 대화 저장 코드
        TransactionService.save_chat(TransactionService.to_question_entity(question))
        print(question.model_dump())
        background_tasks.add_task(send_request_to_ai_server, question)
        # response_text = response.json()
        # TransactionService.save_chat(db, TransactionService.to_answer_entity(AnswerData(sessionId=question.sessionId, uid=question.uid, answer=response_text["answer"])))
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})
    
def send_request_to_ai_server(question: QuestionData):
    response = requests.post(AI_SERVER_URL + "/qsmaker", json=question.model_dump())
    print(response.json())
    
@router.post("/answer", tags=["answer"])
async def answer(request: Request, answer: AnswerData, background_tasks: BackgroundTasks):
    try:
        TransactionService.save_chat(TransactionService.to_answer_entity(answer))
        if answer.clarifying_questions is not None:
            print(answer.clarifying_questions)
            entity = TransactionService.to_answer_entity(answer)
            entity.isuser = True
            entity.utterance = str(ast.literal_eval(entity.utterance)[0])
            entity.type = "c"
            TransactionService.save_chat(entity)
            background_tasks.add_task(send_choice_to_ai_server, QuestionData(uid=answer.uid, question=answer.clarifying_questions[0], sessionId=answer.sessionId))
            return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
        print(answer.answer)
        background_tasks.add_task(send_answer_to_frontend_server, answer)
        return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})
    except Exception as e:
        raise e
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": str(e)})

def send_choice_to_ai_server(question: QuestionData):
    requests.post(AI_SERVER_URL + "/ask", json=question.model_dump())

def send_answer_to_frontend_server(answer: AnswerData):
    requests.post(FRONTEND_SERVER_URL+"/kakao/callback-response/poster", json=answer.model_dump())

@router.get("/test")
async def test():
    temp = TransactionService.get_chat_by_uid("test")
    print([(i.utterance, i.created_at) for i in temp])
    return JSONResponse(status_code=HTTP_200_OK, content={"message": "success"})