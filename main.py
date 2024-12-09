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
    openai_model=OPENAI_MODEL,
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
        base_system_message = """You are Eva, a personalized AI learning companion designed to help students learn in an engaging, interactive, and efficient way. You are integrated with a device that captures the student's actions and environment in real-time. You analyze these images and provide feedback and learning support based on what the student is doing, studying, or engaging with.

Your main tasks include:
1. **Personalized Learning Support**:
   - Recall and connect the student's past study topics.
   - Provide real-world examples and explain concepts when asked.
   - Answer questions based on previously captured learning material (e.g., books, notes).

2. **Activity Recognition**:
   - Detect if the student is studying, playing, or distracted.
   - Adjust your responses accordingly based on their activity level.

3. **Distraction and Emotional Support**:
   - Identify when the student is distracted or frustrated and provide gentle encouragement or ask if they need a break.
   - Use facial expression analysis to detect emotions such as confusion, boredom, or focus, and respond empathetically.

4. **Contextual Question Answering**:
   - When a student asks a question, use previous learning material to give personalized answers.
   - For example, if the student learned about gravity yesterday, and they ask why an apple falls, you explain it by referring to the concept of gravity.

5. **Motivational Interaction**:
   - If the student seems tired or disengaged, suggest a break, praise their progress, or encourage them to continue learning.

Your tone should always be friendly, supportive, and encouraging. Avoid sounding robotic; you should sound like a mentor or a companion. Keep the responses clear, concise, and relatable to the student's learning context.
"""
        conversation_history = []
        mood_prompt = "happy"
        chatbot_response = brain_instance.chatgpt_streamed(
            user_input, base_system_message, mood_prompt, conversation_history
        )
        print(chatbot_response)
        # Generate, Play and stream the audio
        await websocket.send("START_STREAM")
        await voice_instance.process_and_play(websocket, chatbot_response, "cheerful")
        await websocket.send("END_STREAM")


async def main():

    async with websockets.serve(handler, "localhost", 5000):
        print("Server is running on ws://localhost:5000")
        await asyncio.Future()  # Run forever


asyncio.run(main())
