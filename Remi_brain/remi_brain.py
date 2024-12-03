import requests
import json
class remi_brain:
    def __init__(self, model_provider, ollama_model, ollama_base_url, openai_api_key, openai_base_url, openai_model):
        self.MODEL_PROVIDER = model_provider
        self.OLLAMA_MODEL = ollama_model
        self.OLLAMA_BASE_URL = ollama_base_url
        self.OPENAI_API_KEY = openai_api_key
        self.OPENAI_BASE_URL = openai_base_url
        self.OPENAI_MODEL = openai_model
        self.NEON_GREEN = "\033[92m"
        self.RESET_COLOR = "\033[0m"
    def chatgpt_streamed(self,user_input, system_message, mood_prompt, conversation_history):
        if self.MODEL_PROVIDER == "ollama":
            headers = {
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_message + "\n" + mood_prompt}
                ]
                + conversation_history
                + [{"role": "user", "content": user_input}],
                "stream": True,
                "options": {"num_predict": -2, "temperature": 1.0},
            }
            response = requests.post(
                f"{self.OLLAMA_BASE_URL}/v1/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=30,
            )
            response.raise_for_status()

            full_response = ""
            line_buffer = ""
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data:"):
                    line = line[5:].strip()  # Remove the "data:" prefix
                if line:
                    try:
                        chunk = json.loads(line)
                        delta_content = chunk["choices"][0]["delta"].get("content", "")
                        if delta_content:
                            line_buffer += delta_content
                            if "\n" in line_buffer:
                                lines = line_buffer.split("\n")
                                for line in lines[:-1]:
                                    print(self.NEON_GREEN + line + self.RESET_COLOR)
                                    full_response += line + "\n"
                                line_buffer = lines[-1]
                    except json.JSONDecodeError:
                        continue
            if line_buffer:
                print(self.NEON_GREEN + line_buffer + self.RESET_COLOR)
                full_response += line_buffer
            return full_response

        elif self.MODEL_PROVIDER == "openai":
            messages = (
                [{"role": "system", "content": system_message + "\n" + mood_prompt}]
                + conversation_history
                + [{"role": "user", "content": user_input}]
            )
            headers = {
                "Authorization": f"Bearer {self.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {"model": self.OPENAI_MODEL, "messages": messages, "stream": True}
            response = requests.post(
                self.OPENAI_BASE_URL, headers=headers, json=payload, stream=True, timeout=30
            )
            response.raise_for_status()

            full_response = ""
            print("Starting OpenAI stream...")
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data:"):
                    line = line[5:].strip()  # Remove the "data:" prefix
                if line:
                    try:
                        chunk = json.loads(line)
                        delta_content = chunk["choices"][0]["delta"].get("content", "")
                        if delta_content:
                            print(
                                self.NEON_GREEN + delta_content + self.RESET_COLOR, end="", flush=True
                            )
                            full_response += delta_content
                    except json.JSONDecodeError:
                        continue
            print("\nOpenAI stream complete.")
            return full_response    