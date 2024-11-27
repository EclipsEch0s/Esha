import os
import json
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

    # Use to get the response of a given prompt usign llama model of GROQ API
    def Brain(self, prompt):
        msg = {"role": "user", "content": prompt}
        self.messages.append(msg)
        completion = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=self.messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        assistent_content = str()
        for chunk in completion:
            # print(chunk.choices[0].delta.content or "", end="")
            assistent_content += str(chunk.choices[0].delta.content or "")
        msg = {"role": "assistant", "content": assistent_content}
        self.messages.append(msg)
        return assistent_content
        # for chunk in completion:
        # print(chunk.choices[0].delta.content or "", end="")

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
            propmt = input("\n>> ")
            ans = esha.Brain(prompt=propmt)
            print(ans)
    except KeyboardInterrupt:
        ans = esha.Brain("Bye")
        print(ans)
