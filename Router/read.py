from fastapi.responses import JSONResponse, StreamingResponse
import requests
from starlette.status import *
import os
from dotenv import load_dotenv
from fastapi import Request, Form
from Service.aes_service import AesService
from fastapi import APIRouter
from Data.tts import TTSData
from gtts import gTTS
import io

router = APIRouter(prefix="/tts", tags=["tts"])

@router.post("/read")
async def compare_and_generate_tts(request: Request, data: TTSData):
    # AesService.sha1(AesService.encrypt(data.string))
    print(data.key)
    print(AesService.sha1(AesService.encrypt(data.string)))
    if data.key != AesService.sha1(AesService.encrypt(data.string)):
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": "Unauthorized"})
    string = data.string.replace("**", "")
    tts = gTTS(text=string, lang='ko')
    tts_io = io.BytesIO()
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    
    return StreamingResponse(tts_io, media_type="audio/mpeg")
