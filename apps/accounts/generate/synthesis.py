import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

def synthesize_audio(input: str):
    # Initialize the Eleven Labs client
    load_dotenv()
    client = ElevenLabs(
      api_key = os.getenv("ELEVENLABS_API_KEY"),
    )
    # Create an audio generator
    audio = client.text_to_speech.stream(
        text = input,
        
        # Voice IDs
        # Brittney - "kPzsL2i3teMYv0FxEYQ6"
        # Juniper  - "aMSt68OGf4xUZAnLpTU8"
        # Clara    - "Qggl4b0xRMiqOwhPtVWT"
        # Arabella - "Z3R5wn05IrDiVCyEkUrK"
        # Jessica Anne - "lxYfHSkYm1EzQzGhdbfc"
        # Nicole - "piTKgcLEGmPE4e6mEKli"

        voice_id = "Z3R5wn05IrDiVCyEkUrK",
        voice_settings = VoiceSettings(
            stability=1.0,
            use_speaker_boost=False,
            similarity_boost=1.0,
            style=0.0,
            speed=0.76,
        ),
        model_id = "eleven_multilingual_v2",
    )

    # Iterate through the generator returned to collect audio bytes
    meditation = b''
    for chunk in audio:
        if chunk:
            meditation += chunk

    return meditation