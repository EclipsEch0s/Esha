import json
import sys
import os
import pyttsx3 # Still needed if you want TTS on the backend (e.g., for debugging or server-side audio)
import speech_recognition as sr # Still needed if you want STT on the backend
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS for cross-origin requests
from google import genai
from google.genai import types

# --- Esha AI Agent Class (Copied from your previous immersive for self-containment) ---
class Esha:
    def __init__(self):
        self.r = sr.Recognizer()

        # Initialize Generative AI client using the 'google-genai' library's structure
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Fallback to a hardcoded key if environment variable not set.
            # IMPORTANT: Replace "YOUR_ACTUAL_GEMINI_API_KEY_HERE" with your real API key
            # if you are running this locally and not using environment variables.
            api_key = "YOUR_ACTUAL_GEMINI_API_KEY_HERE"
            print("[WARNING: GEMINI_API_KEY environment variable not set. Using hardcoded key (for testing only).]")

        try:
            self.genai_client = genai.Client(api_key=api_key)
            self.gemini_model = "gemini-2.0-flash"
            print("['google-genai' client initialized successfully.]")
        except Exception as e:
            print(f"[!] Failed to initialize 'google-genai' client: {e}")
            print("Please ensure your API key is correct and `google-genai` is installed.")
            sys.exit(1)

        self.messages = []
        self.SetSystemMessage() # This will set self._system_instruction_content

        try:
            self.LoadMemory()
        except FileNotFoundError:
            print("[Memory file not found. Starting with empty conversation.]")
        except json.JSONDecodeError:
            print("[!] Error loading memory: 'memory.json' is corrupted or empty. Starting with empty conversation.")
            self.messages = []
        except Exception as e:
            print(f"[!] An unexpected error occurred while loading memory: {e}")
            self.messages = []


    def SetSystemMessage(self):
        """
        Loads the system instruction content from 'system.txt' and stores it in self._system_instruction_content.
        It does NOT add it to self.messages, as it will be passed via system_instruction in the API call.
        """
        try:
            with open("system.txt", "r") as file:
                content = file.read()
            with open("user.json", "r") as userData:
                data = json.load(userData)
                content = content.replace("{name}", data.get("name", "User"))
                content = content.replace("{age}", str(data.get("age", "unknown")))
                content = content.replace("{gender}", data.get("gender", "unknown"))
                content = content.replace("{location}", data.get("location", "unknown"))
                self._system_instruction_content = content
        except FileNotFoundError as e:
            print(f"[!] Configuration file missing: {e}. Please ensure 'system.txt' and 'user.json' exist.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("[!] Error parsing 'user.json'. Please ensure it's valid JSON.")
            sys.exit(1)
        except Exception as e:
            print(f"[!] An unexpected error occurred while setting system message: {e}")
            sys.exit(1)


    def Brain(self, prompt):
        """
        Sends the user's prompt to the Gemini 2.0 Flash model and gets a reply using the 'google-genai' library.
        Manages the conversation history (self.messages).
        """
        self.messages.append({"role": "user", "content": prompt})

        try:
            formatted_contents = []
            for message in self.messages:
                formatted_contents.append(
                    types.Content(
                        role=message["role"],
                        parts=[types.Part.from_text(text=message["content"])]
                    )
                )

            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=512,
                response_mime_type="text/plain",
                system_instruction=[types.Part.from_text(text=self._system_instruction_content)],
            )

            full_reply_content = ""
            print("--- Streaming response from Gemini (via 'google-genai') ---")
            for chunk in self.genai_client.models.generate_content_stream(
                model=self.gemini_model,
                contents=formatted_contents,
                config=generate_content_config,
            ):
                text_part = chunk.text
                if text_part:
                    print(text_part, end="")
                    full_reply_content += text_part
            print("\n---------------------------------------------------------")

            if full_reply_content:
                print(f"[Esha] {full_reply_content}")
                self.messages.append({"role": "model", "content": full_reply_content})
                return full_reply_content
            else:
                print("[!] Gemini API stream did not return any text.")
                return "Sorry, I couldn't get a valid response from the AI."

        except Exception as e:
            print(f"[!] API interaction error with 'google-genai': {e}")
            return "Sorry, I'm having trouble communicating with the AI service. Please check your API key and connection."

    def SaveMemory(self):
        """
        Saves the current conversation history (excluding the system message, as it's handled separately) to 'memory.json'.
        """
        try:
            with open("memory.json", "w") as file:
                json.dump(self.messages, file, indent=4)
            print("[Memory saved.]")
        except Exception as e:
            print(f"[!] Error saving memory: {e}")

    def LoadMemory(self):
        """
        Loads conversation history from 'memory.json' and appends it to self.messages.
        Ensures only 'user' and 'model' roles are loaded, as system message is handled via system_instruction.
        """
        with open("memory.json", "r") as file:
            loaded_messages = json.load(file)

        chat_history = [m for m in loaded_messages if m.get("role") != "system"]

        if chat_history:
            self.messages.extend(chat_history)
            print("[Memory loaded.]")
        else:
            print("[Memory file found, but no conversation history loaded.]")

    def TextToSpeechWithPYttsx3(self, sentence):
        # This function is typically for local audio output, not for a web API response.
        # Keeping it here for completeness of the Esha class, but it won't be used
        # directly by the Flask API for sending audio to the frontend.
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.setProperty("volume", 1.0)
            voices = engine.getProperty("voices")
            if voices:
                engine.setProperty("voice", voices[0].id)
            else:
                print("[!] No voices found for pyttsx3. Using default.")
            engine.say(sentence)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[!] TTS Error: {e}. Please ensure pyttsx3 is correctly installed and configured.")

    def SpeechToTextWithSpeech_recognition(self):
        # This function is typically for local microphone input, not for a web API.
        # Frontend will handle speech-to-text if needed.
        return "" # Placeholder as it's not used in this API context

if __name__ == "__main__":
    esha = Esha()
    esha.Brain("Hi");