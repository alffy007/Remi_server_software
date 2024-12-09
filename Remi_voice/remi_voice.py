import os
import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
import pyaudio
import wave
import time
import asyncio
import websockets
import socket


ckpt_base = 'Remi_voice/checkpoints_v2/base_speakers/EN'
ckpt_converter = 'Remi_voice/checkpoints_v2/converter'
device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = 'outputs'
print(f"Using device: {device}")
base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

os.makedirs(output_dir, exist_ok=True)

source_se = torch.load(f'{ckpt_base}/en_style_se.pth').to(device)

reference_speaker = 'Remi_voice/missminutes.mp3'  # This is the voice you want to clone
target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='Remi_voice/processed', vad=True)

save_path = f'{output_dir}/output_en_default.wav'


# Function to play audio in chunks using PyAudio
async def stream_audio(websocket,file_path):
    # Open the audio file
    wf = wave.open(file_path, "rb")
    # Create a PyAudio instance
    # p = pyaudio.PyAudio()
    print("rate",wf.getframerate())
    # print("format",p.get_format_from_width(wf.getsampwidth()))
    print("channels",wf.getnchannels())
    # Open a stream to play audio
    # stream = p.open(
    #     format=p.get_format_from_width(wf.getsampwidth()),
    #     channels=wf.getnchannels(),
    #     rate=wf.getframerate(),
    #     output=True,
    # )

    # Stream and play the audio chunk by chunk
    chunk_size = 100000
    # data = wf.readframes(chunk_size)
    # while data:
    #     await websocket.send(data)
    #     stream.write(data)  # Write the audio chunk to the stream
    #     data = wf.readframes(chunk_size)  # Read the next chunk
    #     time.sleep(0.01)  # Add a short delay to simulate real-time streaming
    while True:
        data = wf.readframes(chunk_size)
        if not data:
            break
        await websocket.send(data)
        # await asyncio.sleep(0.01)

    # Stop and close the stream and PyAudio instance
    # stream.stop_stream()
    # stream.close()
    # p.terminate()

def stream_audio_udp(file_path, host='0.0.0.0', port=12345):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with wave.open(file_path, 'rb') as wf:
        chunk_size = 1024
        while data := wf.readframes(chunk_size):
            sock.sendto(data, (host, port))
    sock.close()


class RemiVoice:
    async def process_and_play(self,websocket, text, tts_mod):
        src_path = f'{output_dir}/tmp.wav'
        
        # Step 1: Generate the speech (TTS)
        print("Generating speech...")
        base_speaker_tts.tts(text, src_path, speaker=tts_mod, language='English', speed=1.1)
        
        # Step 2: Run the tone color converter to match the target speaker
        print("Converting tone color...")
        encode_message = "@MyShell" 
        tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=save_path,
            message=encode_message
        )
        print("Audio generated successfully with OpenVoice.")

        # Step 3: Stream the audio while it's being generated
        print("Streaming audio in real-time...")
        await stream_audio(websocket,save_path)


# Example usage
# remi = RemiVoice()
# remi.process_and_play("Hello, how are you feeling today?", tts_mod="default")
