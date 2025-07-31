from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Literal
import re
from generation import generate_script
from synthesis import synthesize_audio
from music import mix_music
from elevenlabs.core.api_error import ApiError

class Request(BaseModel):
    # User Info
    name: str
    goals: str
    dreamlife: str
    dream_activities: str

    # Ritual Info
    ritual_type: Literal["Story", "Guided"]
    tone: Literal["Dreamy", "ASMR"]
    voice: Literal["female", "male"]
    length: Literal[2, 5, 10]
    check_in: str = None

vela = FastAPI()


@vela.post("/sleep")
def sleep(request: Request):
    script = generate_script(request.name, 
                             request.goals, 
                             request.dreamlife, 
                             request.dream_activities, 
                             get_word_count(request.length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    try:
        synthesis = synthesize_audio(pauses, request.voice)
    except ApiError as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs API Error: {e.body['detail']['message']}")
    mixed_audio = mix_music(synthesis)
    
    return Response(
        content=mixed_audio,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=sleep_manifestation.wav"}
    )


@vela.post("/spark")
def spark(request: Request):
    script = generate_script(request.name, 
                             request.goals, 
                             request.dreamlife, 
                             request.dream_activities, 
                             get_word_count(request.length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    try:
        synthesis = synthesize_audio(pauses, request.voice)
    except ApiError as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs API Error: {e.body['detail']['message']}")
    mixed_audio = mix_music(synthesis)
    
    return Response(
        content=mixed_audio,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=morning_spark.wav"}
    )


@vela.post("/calm")
def calm(request: Request):
    script = generate_script(request.name, 
                             request.goals, 
                             request.dreamlife, 
                             request.dream_activities, 
                             get_word_count(request.length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    try:
        synthesis = synthesize_audio(pauses, request.voice)
    except ApiError as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs API Error: {e.body['detail']['message']}")
    mixed_audio = mix_music(synthesis)
    
    return Response(
        content=mixed_audio,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=calming_reset.wav"}
    )


@vela.post("/dream")
def dream(request: Request):
    script = generate_script(request.name, 
                             request.goals, 
                             request.dreamlife, 
                             request.dream_activities, 
                             get_word_count(request.length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    try:
        synthesis = synthesize_audio(pauses, request.voice)
    except ApiError as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs API Error: {e.body['detail']['message']}")
    mixed_audio = mix_music(synthesis)
    
    return Response(
        content=mixed_audio,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=dream_visualizer.wav"}
    )


@vela.post("/check-in")
def check_in(request: Request):
    script = generate_script(request.name, 
                             request.goals, 
                             request.dreamlife, 
                             request.dream_activities, 
                             get_word_count(request.length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    try:
        synthesis = synthesize_audio(pauses, request.voice)
    except ApiError as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs API Error: {e.body['detail']['message']}")
    mixed_audio = mix_music(synthesis)
    
    return Response(
        content=mixed_audio,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=check_in.wav"}
    )


def get_word_count(mins: int):
    # Speech Rate = 114 words/minute
    # 2 mins = 230
    # 5 mins = 570 
    # 10 mins = 1,140
    # 15 mins = 1,700
    # 20 mins = 2,270
    match mins:
        case 2:
            return "250"
        case 5:
            return "600"
        case 10:
            return "1200"