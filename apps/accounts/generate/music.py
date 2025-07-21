import io
import os
import logging

logger = logging.getLogger(__name__)

def convert_wav_to_mp3(wav_file_path, output_path=None):
    """
    Convert a .wav file to .mp3 format.
    
    Args:
        wav_file_path (str): Path to the input .wav file
        output_path (str, optional): Path for the output .mp3 file. 
                                   If not provided, will use same name with .mp3 extension
    
    Returns:
        str: Path to the converted .mp3 file
    """
    try:
        from pydub import AudioSegment
        
        # Set up ffprobe path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        AudioSegment.ffprobe = os.path.join(base_dir, "ffprobe.exe")
        
        # Load the .wav file
        audio = AudioSegment.from_wav(wav_file_path)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = wav_file_path.rsplit('.', 1)[0] + '.mp3'
        
        # Export as .mp3
        audio.export(output_path, format="mp3")
        
        logger.info(f"Successfully converted {wav_file_path} to {output_path}")
        return output_path
        
    except ImportError as e:
        logger.error(f"pydub library not available: {e}")
        raise ImportError("pydub library is required for audio conversion")
    except Exception as e:
        logger.error(f"Error converting .wav to .mp3: {e}")
        raise

def convert_wav_bytes_to_mp3(wav_bytes):
    """
    Convert .wav bytes to .mp3 bytes.
    
    Args:
        wav_bytes (bytes): Raw .wav file bytes
    
    Returns:
        bytes: Converted .mp3 file bytes
    """
    try:
        from pydub import AudioSegment
        
        # Set up ffprobe path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        AudioSegment.ffprobe = os.path.join(base_dir, "ffprobe.exe")
        
        # Load .wav from bytes
        audio = AudioSegment.from_wav(io.BytesIO(wav_bytes))
        
        # Export to bytes buffer
        buffer = io.BytesIO()
        audio.export(buffer, format="mp3")
        buffer.seek(0)
        
        logger.info("Successfully converted .wav bytes to .mp3 bytes")
        return buffer.read()
        
    except ImportError as e:
        logger.error(f"pydub library not available: {e}")
        raise ImportError("pydub library is required for audio conversion")
    except Exception as e:
        logger.error(f"Error converting .wav bytes to .mp3: {e}")
        raise

def mix_music(meditation, input_format="mp3"):
    """
    Mix meditation audio with background music.
    Supports both WAV and MP3 input formats.
    Fallback implementation when pydub is not available.
    
    Args:
        meditation: Audio bytes (WAV or MP3)
        input_format: Format of input audio ("wav" or "mp3")
    """
    try:
        from pydub import AudioSegment
        
        # AudioSegment.converter = ffmpeg_path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        AudioSegment.ffprobe = os.path.join(base_dir, "ffprobe.exe") 
        
        # Load audio file
        music = AudioSegment.from_file("music.mp3")
        
        # Load speech audio - detect format automatically or use specified format
        if input_format.lower() == "wav":
            speech_original = AudioSegment.from_wav(io.BytesIO(meditation))
        else:
            # Try to auto-detect format, fallback to mp3
            try:
                speech_original = AudioSegment.from_file(io.BytesIO(meditation), format="wav")
            except:
                speech_original = AudioSegment.from_file(io.BytesIO(meditation), format="mp3")
        
        speech = change_speed(speech_original)

        # Add delay to speech (5s of silence at the beginning)
        speech = AudioSegment.silent(duration=5000) + speech

        # Adjust music to match new length
        music_duration = len(speech) + 20000
        music = music[:music_duration]

        # Adjust volume
        speech = speech - 4
        music = music - 6

        # Fade music
        music = music.fade_in(3000).fade_out(20000)

        # Overlay speech on top music
        combined = music.overlay(speech)

        # Return Bytes - always export as MP3 for smaller file size
        buffer = io.BytesIO()
        combined.export(buffer, format="mp3")
        buffer.seek(0)

        return buffer.read()
        
    except ImportError as e:
        logger.warning(f"pydub not available: {e}. Using fallback implementation.")
        return _fallback_mix_music(meditation)
    except Exception as e:
        logger.error(f"Error in pydub audio processing: {e}. Using fallback implementation.")
        return _fallback_mix_music(meditation)

def _fallback_mix_music(meditation):
    """
    Fallback implementation that returns the original meditation audio
    without mixing with background music.
    """
    logger.info("Using fallback audio mixing - returning original meditation audio")
    return meditation

def change_speed(audio_segment, speed=0.98):
    """
    Change the speed of an audio segment.
    """
    try:
        new_frame_rate = int(audio_segment.frame_rate * speed)
        slowed = audio_segment._spawn(audio_segment.raw_data, overrides={
            "frame_rate": new_frame_rate
        }).set_frame_rate(audio_segment.frame_rate)
        return slowed
    except Exception as e:
        logger.warning(f"Could not change audio speed: {e}. Returning original audio.")
        return audio_segment

def convert_audio_to_mp3(audio_bytes, input_format="auto"):
    """
    Convert audio bytes to MP3 format.
    
    Args:
        audio_bytes: Raw audio bytes
        input_format: Input format ("wav", "mp3", or "auto" for auto-detection)
    
    Returns:
        bytes: MP3 audio bytes
    """
    try:
        from pydub import AudioSegment
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        AudioSegment.ffprobe = os.path.join(base_dir, "ffprobe.exe")
        
        # Load audio based on format
        if input_format.lower() == "wav":
            audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
        elif input_format.lower() == "mp3":
            audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        else:
            # Auto-detect format
            try:
                audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
            except:
                audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        
        # Export as MP3
        buffer = io.BytesIO()
        audio.export(buffer, format="mp3")
        buffer.seek(0)
        
        logger.info(f"Successfully converted audio to MP3 format")
        return buffer.read()
        
    except ImportError as e:
        logger.error(f"pydub library not available: {e}")
        raise ImportError("pydub library is required for audio conversion")
    except Exception as e:
        logger.error(f"Error converting audio to MP3: {e}")
        raise