import json
import pyttsx3
import speech_recognition as sr
from pathlib import Path
from groq import Groq


class Esha:
    def __init__(self) -> None:
        # Gettign the API Keys
        with open("secret_key.json") as file:
            data = json.load(file)
        self.SetSystemMessage()
        #  Setting the groq api
        self.client = Groq(api_key=data["groq"])
        # Setting speech Recognizer
        self.r = sr.Recognizer()
        # Setting up the Paths
        self.SetPaths()
        # Setting Up Existing project details created by ESHA
        self.SetExistingProjectDetails()

    def SetSystemMessage(self):
        with open("./system.txt") as file:
            content = file.read()
            with open("user.json") as userData:
                data = json.load(userData)
                content = content.replace("{name}", data["name"])
                content = content.replace("{age}", data["age"])
                content = content.replace("{gender}", data["gender"])
                content = content.replace("{location}", data["location"])
                self.messages = [
                    {
                        "role": "system",
                        "content": content,
                    }
                ]

    # Use to get the response of a given prompt usign llama model of GROQ API
    def Brain(self, prompt):
        msg = {"role": "user", "content": prompt}
        self.messages.append(msg)
        completion = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=self.messages,
            temperature=1.5,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        assistent_content = str()
        for chunk in completion:
            word = chunk.choices[0].delta.content or ""
            print(word, end="")
            assistent_content += str(word)
        msg = {"role": "assistant", "content": assistent_content}
        self.messages.append(msg)
        return assistent_content

    def TextToSpeechWithPYttsx3(self, sentence):
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        engine.setProperty("voice", engine.getProperty("voices")[1].id)
        engine.say(sentence)
        engine.runAndWait()

    def SpeechToTextWithSpeech_recognition(self):
        with sr.Microphone() as source:
            self.r.adjust_for_ambient_noise(source, duration=0.2)
            audio = self.r.listen(source)
            text = self.r.recognize_google(audio)
            text = text.lower()
            print(text)
            return text

    def SetPaths(self):
        home = Path.home()
        desktop = Path.home() / "Desktop"
        documents = Path.home() / "Documents"
        downloads = Path.home() / "Downloads"
        self.Brain(
            f"Set Desktop path = {desktop}, home path = {home}, documents path = {documents}, downloads path = {downloads}"
        )
        # For custom paths 
        with open("paths.json") as file:
            data = json.load(file)
        for i in data:
            self.Brain(
                f"Set {i} path = {data[i]}"
            )

    def SetExistingProjectDetails(self):
        with open("project.json") as file:
            data = json.load(file)
        for i in data:
            self.Brain(f"Set description of the project {i} is {data[i]['desc']} and location is {data[i]['path']}")
