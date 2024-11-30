import os
import json
import pyttsx3
import speech_recognition as sr
from groq import Groq


class Esha:
    def __init__(self) -> None:
        # Gettign the API Keys
        with open("secret_key.json") as file:
            data = json.load(file)
        with open("./system.txt") as file:
            self.messages = [
                {
                    "role": "system",
                    "content": file.read(),
                }
            ]

        #  Setting the groq api
        self.client = Groq(api_key=data["groq"])
        # Setting speech Recognizer
        self.r = sr.Recognizer()

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
        self.TextToSpeechWithPYttsx3(assistent_content)
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

    # For creating Folder
    def CreateFolder(self, path, folderName):
        try:
            os.mkdir(os.path.join(path, folderName))
            return True
        except FileExistsError:
            return "FileExists"
        except PermissionError:
            return "PermissionError"
        except Exception:
            return False

    # For creating Files
    def CreateFile(self, path, fileName):
        filePath = os.path.join(path, fileName)
        if os.path.exists(filePath):
            return "FileExists"
        with open(filePath, "w"):
            return True

    # List Files and Folders in a Directory
    def ReturnFilesNFolderInAPath(self, path):
        try:
            filesNfolders = os.scandir(path)
        except Exception:
            return False, False
        files = []
        folders = []
        for fileNfolder in filesNfolders:
            if fileNfolder.is_file():
                files.append(fileNfolder)
            elif fileNfolder.is_dir():
                folders.append(fileNfolder)
        return files, folders


if __name__ == "__main__":
    esha = Esha()
    try:
        while True:
            try:
                print("\nListening......")
                prompt = esha.SpeechToTextWithSpeech_recognition()
                if "Esha" in prompt or "isha" in prompt:
                    esha.Brain(prompt=prompt)
            except KeyboardInterrupt:
                exit
            except:
                print("\nCan't understand the words!!")
    except KeyboardInterrupt:
        esha.Brain("Bye")