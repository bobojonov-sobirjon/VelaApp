from elevenlabs import ElevenLabs

def check_api_usage(key):
    # Initialize the Eleven Labs client
    client = ElevenLabs(
      api_key = key,
    )   
    
    usage = client.user.subscription.get()
    character_limit = usage.character_limit
    character_count = usage.character_count
    remaining_characters = character_limit - character_count
    return character_limit, character_count, remaining_characters