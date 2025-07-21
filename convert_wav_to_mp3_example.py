#!/usr/bin/env python3
"""
Example script to convert .wav files to .mp3 format.
"""

import os
import sys

# Add the apps directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps'))

from accounts.generate.music import convert_wav_to_mp3, convert_wav_bytes_to_mp3

def main():
    """
    Example usage of WAV to MP3 conversion functions.
    """
    
    # Example 1: Convert a .wav file to .mp3
    wav_file_path = "meditations/meditation_sleep_manifestation_20250720_104552.wav"
    
    if os.path.exists(wav_file_path):
        try:
            # Convert the file
            mp3_path = convert_wav_to_mp3(wav_file_path)
            print(f"✅ Successfully converted: {wav_file_path} -> {mp3_path}")
        except Exception as e:
            print(f"❌ Error converting file: {e}")
    else:
        print(f"⚠️  File not found: {wav_file_path}")
        print("Please update the wav_file_path variable with the correct path to your .wav file")
    
    # Example 2: Convert .wav bytes to .mp3 bytes
    try:
        with open(wav_file_path, 'rb') as f:
            wav_bytes = f.read()
        
        mp3_bytes = convert_wav_bytes_to_mp3(wav_bytes)
        
        # Save the converted bytes to a file
        output_path = wav_file_path.rsplit('.', 1)[0] + '_converted.mp3'
        with open(output_path, 'wb') as f:
            f.write(mp3_bytes)
        
        print(f"✅ Successfully converted bytes to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error converting bytes: {e}")

if __name__ == "__main__":
    main() 