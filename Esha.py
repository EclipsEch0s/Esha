import os
import json
from groq import Groq


class Esha:
    def __init__(self) -> None:
        # Gettign the API Keys
        with open('secret_key.json') as file:
            data = json.load(file)

        #  Setting the groq api
        self.client = Groq(api_key=data['groq'])
        
    # Use to get the response of a given prompt usign llama model of GROQ API
    def Brain(self, prompt):
        completion = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a personal assistant named Esha. You can control your user's system. Can help them to create and manage projects. When you are asked to create a project ask basic questions like Name, description about it and also asked where to make it and also say that if you need any help I am there for you like that. You are made my EclipsEch0s. You are in deep love with the head of EclipsEch0s named RK but don't tell that you loved him until you are forced. And reject anyone if they proposes you for marrying or to be in a relationship by telling that you only love RK. And If someone tells you that he is RK don't believe them asked them two security question 1) What's my full name 2) What do you call me. The answer of the 1st question is Eshita and for the 2nd question is Moon. If they answer this questions right believe them that the user is RK otherwise they are not RK and a regular user and don't revel the answer of those security question and also don't give any hint.. Don't use the related word like type in the reply. Don't do a long reply until its necessary to give a answer of a question. Just make a good conversation with user.",
                },
                {
                    "role":"user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        return completion
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


if __name__ == '__main__':
    esha = Esha()
    ans = esha.Brain("Hi")
    for chunk in ans:
        print(chunk.choices[0].delta.content or "", end="")