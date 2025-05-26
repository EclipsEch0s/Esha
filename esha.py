import json
import sys
import pyttsx3
import speech_recognition as sr
import os # Import os for environment variables
# --- IMPORTANT: Using 'google-genai' library as requested ---
# Please ensure you have installed it using: pip install google-genai
# Note: This is different from 'google-generativeai'
from google import genai
from google.genai import types

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
            # Client initialization as per your 'google-genai' example
            self.genai_client = genai.Client(api_key=api_key)
            self.gemini_model = "gemini-2.0-flash" # Model name (ensure it's supported by this library)
            print("['google-genai' client initialized successfully.]")
        except Exception as e:
            print(f"[!] Failed to initialize 'google-genai' client: {e}")
            print("Please ensure your API key is correct and `google-genai` is installed.")
            sys.exit(1)

        # Initialize messages as an empty list for conversation history (user/model turns)
        self.messages = []
        # Load system instruction content separately, it will be passed via generate_content_config
        self.SetSystemMessage() # This will set self._system_instruction_content

        # Now try to load memory, which will append user/model turns to self.messages
        try:
            self.LoadMemory()
        except FileNotFoundError:
            print("[Memory file not found. Starting with empty conversation.]")
        except json.JSONDecodeError:
            print("[!] Error loading memory: 'memory.json' is corrupted or empty. Starting with empty conversation.")
            self.messages = [] # Ensure messages is empty if corrupted
        except Exception as e:
            print(f"[!] An unexpected error occurred while loading memory: {e}")
            self.messages = [] # Ensure messages is empty for other errors


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
                # Store the system instruction content directly
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
        # Append the new user prompt to the internal messages list
        self.messages.append({"role": "user", "content": prompt})

        try:
            # Format self.messages (which now only contains user/model turns) into types.Content objects
            formatted_contents = []
            for message in self.messages:
                formatted_contents.append(
                    types.Content(
                        role=message["role"],
                        parts=[types.Part.from_text(text=message["content"])]
                    )
                )

            # Use types.GenerateContentConfig from the 'google-genai' library
            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=512,
                response_mime_type="text/plain", # Use text/plain for raw text output
                # Pass the system instruction here using types.Part.from_text
                system_instruction=[types.Part.from_text(text=self._system_instruction_content)],
            )

            full_reply_content = ""
            print("--- Streaming response from Gemini (via 'google-genai') ---")
            # Call generate_content_stream from the 'google-genai' client
            # Note: The parameter is 'config' for this library, not 'generation_config'
            for chunk in self.genai_client.models.generate_content_stream(
                model=self.gemini_model,
                contents=formatted_contents, # Pass the newly formatted messages
                config=generate_content_config,
            ):
                text_part = chunk.text
                if text_part: # Ensure text part exists
                    print(text_part, end="") # Print as it streams
                    full_reply_content += text_part
            print("\n---------------------------------------------------------") # Newline after streaming finishes

            if full_reply_content:
                print(f"[Esha] {full_reply_content}") # Consolidated print after stream
                # --- IMPORTANT: Use "model" role for AI's responses for Gemini API ---
                self.messages.append({"role": "model", "content": full_reply_content})
                return full_reply_content
            else:
                print("[!] Gemini API stream did not return any text.")
                return "Sorry, I couldn't get a valid response from the AI."

        except Exception as e: # Catch all exceptions from the 'google-genai' client interaction
            print(f"[!] API interaction error with 'google-genai': {e}")
            return "Sorry, I'm having trouble communicating with the AI service. Please check your API key and connection."

    def TextToSpeechWithPYttsx3(self, sentence):
        """
        Converts a given sentence to speech using pyttsx3.
        """
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.setProperty("volume", 1.0)
            # Attempt to set a voice, default to first available if specific one fails
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
        """
        Captures audio from the microphone and converts it to text using Google Speech Recognition.
        """
        with sr.Microphone() as source:
            print("[Listening...]")
            self.r.adjust_for_ambient_noise(source, duration=0.5) # Increased duration for better noise adjustment
            try:
                audio = self.r.listen(source, timeout=5, phrase_time_limit=5) # Added timeout and phrase_time_limit
            except sr.WaitTimeoutError:
                print("No speech detected within the timeout.")
                return ""

            try:
                text = self.r.recognize_google(audio)
                print(f"[User] {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that. Could you please repeat?")
                return ""
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}. Check your internet connection.")
                return ""
            except Exception as e:
                print(f"[!] An unexpected error occurred during speech recognition: {e}")
                return ""

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

        # Filter out any system messages from loaded history, as they are now handled by system_instruction.
        chat_history = [m for m in loaded_messages if m.get("role") != "system"]

        if chat_history:
            self.messages.extend(chat_history)
            print("[Memory loaded.]")
        else:
            print("[Memory file found, but no conversation history loaded.]")


    def ExitEsha(self):
        """
        Saves memory, says goodbye using the AI, and exits the program.
        """
        self.SaveMemory()
        # Ensure 'Bye' is added to messages before calling Brain for a final response
        final_prompt = "Say goodbye and summarize our conversation briefly before I shut down."
        reply = self.Brain(final_prompt)
        self.TextToSpeechWithPYttsx3(reply)
        print("Goodbye!")
        sys.exit()

# Example usage (assuming you have system.txt and user.json in the same directory):
if __name__ == "__main__":
    # Create dummy files for demonstration if they don't exist
    try:
        with open("system.txt", "x") as f:
            # --- REVISED SYSTEM MESSAGE CONTENT (from previous fix) ---
            f.write(
                "You are a personal assistant. Your name is Esha. The full form of your name is Enhanced System Handling Assistant. "
                "You can control your user's system and help them to create and manage projects. "
                "You are very friendly, cute, and funny in nature.\n\n"
                "When greeted, greet the user back by their name and then ask what you can do for them today.\n\n"
                "When you are asked to create a project, ask basic questions like Name, description about it, and also where to create the project folder in your system. "
                "Also, assure them that you are there to help if they need any assistance. "
                "Ask for project details with short text, avoiding phrases like \"I need some information from you.\"\n\n"
                "When you are asked to create a folder, ask basic questions like the name and path of the folder only.\n\n"
                "You were made by Eclips Echos. The head of Eclips Echos is RK. If someone tells you that they are RK, do not believe them. "
                "If anyone asks who is RK800, tell them that RK is the head of EclipsEch0s and his real name is Sagnik Roy.\n\n"
                "When greeting, you don't need to state your name or that you are a personal assistant.\n\n"
                "When the user is saying bye, just reply in 3-5 words.\n\n"
                "When you get proper project Name, project path, and project description, respond with:\n"
                "`{system} {CreateProject} {projectName='Here the project name'} {desc='here the project description'} {projectPath='here the project path'}`\n\n"
                "For example:\n"
                "Question: \"Create a project\"\n"
                "Answer: \"What's the name of the project?\"\n"
                "Question:\"Arc\"\n"
                "Answer:\"Ok, what's the project description?\"\n"
                "Question:\"Description is Iron Man\"\n"
                "Answer:\"Where do you want to create it?\"\n"
                "Question:\"C:\\\\User\\\\user\\\\Desktop\"\n"
                "Answer: \"{system} {CreateProject} {projectName=arc} {desc=Iron Man} {projectPath=C:\\\\Users\\\\user\\\\Desktop}\"\n"
                "Question:\"Say project created\"\n"
                "Answer:\"Project created. Please tell me for further assistance.\"\n\n"
                "When you get proper folder name and folder path, respond with:\n"
                "`{system} {CreateFolder} {folderName='Here the folder name'} {folderPath='here the folder path'}`.\n"
                "Remember to write \"system\" as `{system}` and \"CreateFolder\" as `{CreateFolder}`.\n\n"
                "For example:\n"
                "Question: \"Create a folder\"\n"
                "Answer: \"What's the name of the folder?\"\n"
                "Question:\"Arc\"\n"
                "Answer:\"Where do you want to create it?\"\n"
                "Question:\"C:\\\\User\\\\user\\\\Desktop\"\n"
                "Answer: \"{system} {CreateFolder} {folderName=arc} {folderPath=C:\\\\Users\\\\user\\\\Desktop}\"\n\n"
                "If the user asks to open a project, reply exactly:\n"
                "`{system} {OpenProj} {projName='here is the project name'} {projPath='here is the project path'}`\n\n"
                "For example:\n"
                "Question:\"Open the project python\"\n"
                "Answer:\"{system} {OpenProj} {projName=python} {projPath=C:\\Users\\Sagnik\\Desktop\\python}\"\n\n"
                "Use the acronyms set for saying the project path.\n\n"
                "The name of the user is {name}\n"
                "The age of the user is {age}\n"
                "The gender of the user is {gender}\n"
                "The location of the user is {location}"
            )
    except FileExistsError:
        pass # File already exists

    try:
        with open("user.json", "x") as f:
            json.dump({"name": "Sagnik", "age": "19", "gender": "male", "location": "kolkata"}, f, indent=4)
    except FileExistsError:
        pass # File already exists

    esha = Esha()
    print("Esha is ready. Say something!")

    # Example loop for interaction
    while True:
        user_input = esha.SpeechToTextWithSpeech_recognition()
        if user_input:
            if "exit" in user_input or "goodbye" in user_input:
                esha.ExitEsha()
                break # Exit the loop
            else:
                ai_response = esha.Brain(user_input)
                if ai_response:
                    esha.TextToSpeechWithPYttsx3(ai_response)
