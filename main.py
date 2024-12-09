import requests
from dotenv import load_dotenv
import os
from Remi_brain.remi_brain import remi_brain
from Remi_voice.remi_voice import RemiVoice
# from flask import Flask, request
import asyncio
import websockets
# Load environment variables
load_dotenv(override=True)

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

print(MODEL_PROVIDER)
print(OLLAMA_MODEL)
print(OPENAI_API_KEY)
brain_instance = remi_brain(
        model_provider=MODEL_PROVIDER,
        ollama_model=OLLAMA_MODEL,
        ollama_base_url=OLLAMA_BASE_URL,
        openai_api_key=OPENAI_API_KEY,
        openai_base_url=OPENAI_BASE_URL,
        openai_model=OPENAI_MODEL
        )
voice_instance = RemiVoice()

# app = Flask(__name__)


# @app.route('/chat', methods=['POST'])
# def handle_post_request():
#     data = request.get_json()
#     user_input = data.get('chat_text')
#     mood_prompt = data.get('mood_prompt')
#     process_chat(user_input=user_input, mood_prompt=mood_prompt)
#     return "Chat processed", 200

# def process_chat(user_input, mood_prompt):
     
#     #  user_input = "Why am i feeling low"
#      base_system_message = "Your Name is Remi, You are an emotional support companion always ready to help the user and make them laugh. Try to keep your responses concise and uplifting. You can ask personal questions to get to know the user better, Like if he says about his friend you can ask about his friend's name or how long they have been friends. You can also ask about his hobbies or interests. You can also ask about his day or how he is feeling. You can also share some jokes or fun facts to make the user laugh."
#     #  mood_prompt = "Happy"
#      conversation_history = []
#      chatbot_response = brain_instance.chatgpt_streamed(
#                 user_input, base_system_message, mood_prompt, conversation_history
#             )
#      print(chatbot_response)
#      voice_instance.process_and_play(chatbot_response, "neutral")
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000)


async def handler(websocket):
    async for user_input in websocket:
        print(f"Received text: {user_input}")
        base_system_message = "Your Name is Remi, You are an emotional support companion always ready to help the user and make them laugh. Try to keep your responses concise and uplifting. You can ask personal questions to get to know the user better, Like if he says about his friend you can ask about his friend's name or how long they have been friends. You can also ask about his hobbies or interests. You can also ask about his day or how he is feeling. You can also share some jokes or fun facts to make the user laugh."
        conversation_history = []
        mood_prompt = 'happy'
        chatbot_response = brain_instance.chatgpt_streamed(
                user_input, base_system_message, mood_prompt, conversation_history
            )
        print(chatbot_response)
        # Generate, Play and stream the audio
        await websocket.send("START_STREAM")
        await voice_instance.process_and_play(websocket,chatbot_response, "cheerful")
        await websocket.send("END_STREAM")



async def main():

    async with websockets.serve(handler, "localhost", 5000):
        print("Server is running on ws://localhost:5000")
        await asyncio.Future()  # Run forever

asyncio.run(main())    