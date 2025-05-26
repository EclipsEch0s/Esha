import json
import sys
import os
import re # Import regex for parsing AI commands
import pyttsx3 # Still needed if you want TTS on the backend (e.g., for debugging or server-side audio)
import speech_recognition as sr # Still needed if you want STT on the backend
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS for cross-origin requests
from google import genai
from google.genai import types

# --- DUMMY System Class (REPLACE WITH YOUR ACTUAL system.py CONTENT) ---
# This placeholder class is here to make the code runnable.
# Your actual System.py likely contains real file system operations.
class System:
    @staticmethod
    def CreateFolder(folderName, path):
        print(f"[System] Attempting to create folder: {folderName} at {path}")
        # Dummy logic:
        if "forbidden" in folderName.lower():
            return "PermissionError" # Simulate permission error
        if folderName == "existing_folder":
            return "FolderExist" # Simulate folder already exists
        if folderName == "proj_exist":
            return "ProjExist" # Simulate project already exists
        print(f"[System] Dummy: Folder '{folderName}' created at '{path}'")
        return True

    @staticmethod
    def ReturnFilesNFolderInAPath(path):
        print(f"[System] Attempting to list contents of path: {path}")
        # Dummy logic:
        if "invalid" in path.lower():
            return False, False # Simulate path not found/invalid
        print(f"[System] Dummy: Listing files/folders in '{path}'")
        return ["dummy_file.txt"], ["dummy_folder"] # Simulate success
# --- END DUMMY System Class ---


# --- Esha AI Agent Class ---
class Esha:
    def __init__(self):
        self.r = sr.Recognizer()

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
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
        self.SetSystemMessage()

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
        Loads the system instruction content from 'system.txt' and stores it.
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
                self.messages.append({"role": "model", "content": full_reply_content})
                return full_reply_content
            else:
                print("[!] Gemini API stream did not return any text.")
                return "Sorry, I couldn't get a valid response from the AI."

        except Exception as e:
            print(f"[!] API interaction error with 'google-genai': {e}")
            return "Sorry, I'm having trouble communicating with the AI service. Please check your API key and connection."

    def SaveMemory(self):
        try:
            with open("memory.json", "w") as file:
                json.dump(self.messages, file, indent=4)
            print("[Memory saved.]")
        except Exception as e:
            print(f"[!] Error saving memory: {e}")

    def LoadMemory(self):
        with open("memory.json", "r") as file:
            loaded_messages = json.load(file)
        chat_history = [m for m in loaded_messages if m.get("role") != "system"]
        if chat_history:
            self.messages.extend(chat_history)
            print("[Memory loaded.]")
        else:
            print("[Memory file found, but no conversation history loaded.]")

    def TextToSpeechWithPYttsx3(self, sentence):
        # This is for local audio output, not for web API response.
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
        return "" # Not used in API context


# --- Helper Functions for AI Commands ---
# These functions will now return strings to be sent back to the frontend.
# They no longer call esha.TextToSpeechWithPYttsx3 directly.

def CreateProject(reply):
    # Regex pattern to extract key-value pairs
    pattern = r"\{(\w+)=([^\}]+)\}"
    matches = re.findall(pattern, reply)
    project = {key: value for key, value in matches}

    projectName = project.get("projectName")
    projectDesc = project.get("desc")
    projectPath = project.get("projectPath")

    print(f"Project Name: {projectName}")
    print(f"Description: {projectDesc}")
    print(f"Project Path: {projectPath}")

    forbiddenProjectNames = ["RK", "rk", "r.k", "R.K"]
    for i in forbiddenProjectNames:
        if i == projectName:
            return "Sorry, I can't create a project with this name."

    chk = System.CreateFolder(folderName=projectName, path=projectPath)
    if chk == True:
        return esha_agent.Brain("Say Project created or something like that")
    elif chk == "ProjExist":
        return esha_agent.Brain("Say project already exists or something like that")
    elif chk == "PermissionError":
        return esha_agent.Brain("Say I don't have proper permission to create a project or something like that")
    elif chk == False:
        return esha_agent.Brain("Say Sorry, I can't create the project. A problem occurred or something like this.")
    return "Unknown error during project creation."


def CreateFolder(reply):
    # Regular expression to find folderName and folderPath
    pattern = r"\{folderName=([^\}]+)\}|\{folderPath=([^\}]+)\}"
    matches = re.findall(pattern, reply)

    folderName = next((match[0] for match in matches if match[0]), None)
    folderPath = next((match[1] for match in matches if match[1]), None)

    print(f"Folder Name = {folderName}")
    print(f"Folder Path = {folderPath}")

    chk = System.CreateFolder(folderName=folderName, path=folderPath)
    if chk == True:
        return esha_agent.Brain("Say Folder created or something like that")
    elif chk == "FolderExist":
        return esha_agent.Brain("Say folder already exists or something like that")
    elif chk == "PermissionError":
        return esha_agent.Brain("Say sorry, I don't have proper permission or something like that")
    elif chk == False:
        return esha_agent.Brain("Say oops, something went wrong, can't create the folder for now or something like that")
    return "Unknown error during folder creation."


def OpenProj(reply):
    # Regular expression pattern to match projName and projPath
    pattern = r"\{projName=([^\}]+)\} \{projPath=([^\}]+)\}"
    match = re.search(pattern, reply)

    if match:
        proj_name = match.group(1)
        proj_path = match.group(2)
        print(f"projName: {proj_name}")
        print(f"projPath: {proj_path}")

        files, folders = System.ReturnFilesNFolderInAPath(
            os.path.join(proj_path, proj_name)
        )
        if files == False and folders == False:
            return esha_agent.Brain("Say OOps, can't open the project or something like that")
        else:
            # You might want to return the list of files/folders to the frontend here
            # For now, just returning a success message.
            # If you need to send file/folder data, you'd modify the jsonify response in /chat endpoint
            return esha_agent.Brain("Say Project Opened or Something like that")
    else:
        print("No match found for OpenProj.")
        return esha_agent.Brain("Say I couldn't understand which project to open or something like that")


# --- Flask Application Setup ---
app = Flask(__name__)
CORS(app)

esha_agent = Esha()

@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"error": "Missing 'prompt' in request"}), 400

    print(f"\n[API Received] User Prompt: {user_prompt}")
    ai_response = esha_agent.Brain(user_prompt)

    # Check if the AI's response contains a system command
    if "{system}" in ai_response:
        if "{CreateProject}" in ai_response:
            final_response_for_frontend = CreateProject(ai_response)
        elif "{CreateFolder}" in ai_response:
            final_response_for_frontend = CreateFolder(ai_response)
        elif "{OpenProj}" in ai_response:
            final_response_for_frontend = OpenProj(ai_response)
        else:
            final_response_for_frontend = "Esha understood a system command but couldn't parse it correctly."
    else:
        # If no system command, the AI's direct response is the final response
        final_response_for_frontend = ai_response

    esha_agent.SaveMemory() # Save memory after each interaction

    return jsonify({"response": final_response_for_frontend})

@app.route('/')
def index():
    return "Esha AI Backend is running!"

if __name__ == '__main__':
    # Create dummy files for demonstration if they don't exist
    try:
        with open("system.txt", "x") as f:
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
        pass

    try:
        with open("user.json", "x") as f:
            json.dump({"name": "Sagnik", "age": "19", "gender": "male", "location": "kolkata"}, f, indent=4)
    except FileExistsError:
        pass

    app.run(debug=True, port=5000)
