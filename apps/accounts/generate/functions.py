import re
from .generation import generate_script
from .synthesis import synthesize_audio
from .music import mix_music
from elevenlabs.core.api_error import ApiError
from typing import Literal


def sleep_function(name: str, goals: str, dreamlife: str, dream_activities: str, 
                  ritual_type: Literal["Story", "Guided"], tone: Literal["Dreamy", "ASMR"], 
                  voice: Literal["Female", "Male"], length: Literal[2, 5, 10], 
                  check_in: str = None):
    """
    Generate sleep manifestation audio using the provided parameters.
    
    Args:
        name: User's name
        goals: User's goals
        dreamlife: User's dream life description
        dream_activities: User's dream activities
        ritual_type: Type of ritual ("Story" or "Guided")
        tone: Audio tone ("Dreamy" or "ASMR")
        voice: Voice type ("Female" or "Male")
        length: Audio length in minutes (2, 5, or 10)
        check_in: Optional check-in text
    
    Returns:
        bytes: Audio data in WAV format
    """
    script = generate_script(name, goals, dreamlife, dream_activities, get_word_count(length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    
    try:
        synthesis = synthesize_audio(pauses)
    except ApiError as e:
        raise Exception(f"ElevenLabs API Error: {e.body['detail']['message']}")
    
    mixed_audio = mix_music(synthesis)
    return mixed_audio


def spark_function(name: str, goals: str, dreamlife: str, dream_activities: str, 
                  ritual_type: Literal["Story", "Guided"], tone: Literal["Dreamy", "ASMR"], 
                  voice: Literal["Female", "Male"], length: Literal[2, 5, 10], 
                  check_in: str = None):
    """
    Generate morning spark audio using the provided parameters.
    
    Args:
        name: User's name
        goals: User's goals
        dreamlife: User's dream life description
        dream_activities: User's dream activities
        ritual_type: Type of ritual ("Story" or "Guided")
        tone: Audio tone ("Dreamy" or "ASMR")
        voice: Voice type ("Female" or "Male")
        length: Audio length in minutes (2, 5, or 10)
        check_in: Optional check-in text
    
    Returns:
        bytes: Audio data in WAV format
    """
    script = generate_script(name, goals, dreamlife, dream_activities, get_word_count(length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    
    try:
        synthesis = synthesize_audio(pauses)
    except ApiError as e:
        raise Exception(f"ElevenLabs API Error: {e.body['detail']['message']}")
    
    mixed_audio = mix_music(synthesis)
    return mixed_audio


def calm_function(name: str, goals: str, dreamlife: str, dream_activities: str, 
                 ritual_type: Literal["Story", "Guided"], tone: Literal["Dreamy", "ASMR"], 
                 voice: Literal["Female", "Male"], length: Literal[2, 5, 10], 
                 check_in: str = None):
    """
    Generate calming reset audio using the provided parameters.
    
    Args:
        name: User's name
        goals: User's goals
        dreamlife: User's dream life description
        dream_activities: User's dream activities
        ritual_type: Type of ritual ("Story" or "Guided")
        tone: Audio tone ("Dreamy" or "ASMR")
        voice: Voice type ("Female" or "Male")
        length: Audio length in minutes (2, 5, or 10)
        check_in: Optional check-in text
    
    Returns:
        bytes: Audio data in WAV format
    """
    script = generate_script(name, goals, dreamlife, dream_activities, get_word_count(length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    
    try:
        synthesis = synthesize_audio(pauses)
    except ApiError as e:
        raise Exception(f"ElevenLabs API Error: {e.body['detail']['message']}")
    
    mixed_audio = mix_music(synthesis)
    return mixed_audio


def dream_function(name: str, goals: str, dreamlife: str, dream_activities: str, 
                  ritual_type: Literal["Story", "Guided"], tone: Literal["Dreamy", "ASMR"], 
                  voice: Literal["Female", "Male"], length: Literal[2, 5, 10], 
                  check_in: str = None):
    """
    Generate dream visualizer audio using the provided parameters.
    
    Args:
        name: User's name
        goals: User's goals
        dreamlife: User's dream life description
        dream_activities: User's dream activities
        ritual_type: Type of ritual ("Story" or "Guided")
        tone: Audio tone ("Dreamy" or "ASMR")
        voice: Voice type ("Female" or "Male")
        length: Audio length in minutes (2, 5, or 10)
        check_in: Optional check-in text
    
    Returns:
        bytes: Audio data in WAV format
    """
    script = generate_script(name, goals, dreamlife, dream_activities, get_word_count(length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    
    try:
        synthesis = synthesize_audio(pauses)
    except ApiError as e:
        raise Exception(f"ElevenLabs API Error: {e.body['detail']['message']}")
    
    mixed_audio = mix_music(synthesis)
    return mixed_audio


def check_in_function(name: str, goals: str, dreamlife: str, dream_activities: str, 
                     ritual_type: Literal["Story", "Guided"], tone: Literal["Dreamy", "ASMR"], 
                     voice: Literal["Female", "Male"], length: Literal[2, 5, 10], 
                     check_in: str = None):
    """
    Generate check-in audio using the provided parameters.
    
    Args:
        name: User's name
        goals: User's goals
        dreamlife: User's dream life description
        dream_activities: User's dream activities
        ritual_type: Type of ritual ("Story" or "Guided")
        tone: Audio tone ("Dreamy" or "ASMR")
        voice: Voice type ("Female" or "Male")
        length: Audio length in minutes (2, 5, or 10)
        check_in: Optional check-in text
    
    Returns:
        bytes: Audio data in WAV format
    """
    script = generate_script(name, goals, dreamlife, dream_activities, get_word_count(length))
    pauses = re.sub(r'(?<=\.)\s(?![^.]*\.$)', ' --- ', script)
    
    try:
        synthesis = synthesize_audio(pauses)
    except ApiError as e:
        raise Exception(f"ElevenLabs API Error: {e.body['detail']['message']}")
    
    mixed_audio = mix_music(synthesis)
    return mixed_audio


def get_word_count(mins: int):
    """
    Get the word count based on the audio length in minutes.
    
    Args:
        mins: Length in minutes (2, 5, or 10)
    
    Returns:
        str: Word count as string
    """
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