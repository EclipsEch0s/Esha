import re
import os
import json
from system import System
import signal
import sys

from esha import Esha

esha = Esha()


def CreateProject(reply):
    # Regex pattern to extract key-value pairs
    pattern = r"\{(\w+)=([^\}]+)\}"

    # Find all matches
    matches = re.findall(pattern, reply)

    # Create a dictionary from the matches
    project = {key: value for key, value in matches}

    # Access the project details
    projectName = project.get("projectName")
    projectDesc = project.get("desc")
    projectPath = project.get("projectPath")

    print(f"Project Name: {projectName}")
    print(f"Description: {projectDesc}")
    print(f"Project Path: {projectPath}")
    forbiddenProjectNames = ["RK", "rk", "r.k", "R.K"]
    for i in forbiddenProjectNames:
        if i == projectName:
            esha.TextToSpeechWithPYttsx3("Sorry Can't create project with this name")
            return
    chk = System.CreateFolder(folderName=projectName, path=projectPath)
    if chk == True:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say Project created or something like that")
        )
    elif chk == "ProjExist":
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say project already exist or something like that")
        )
    elif chk == "PermissionError":
        esha.TextToSpeechWithPYttsx3(
            esha.Brain(
                "Say I don't have proper permision to create a project or something like that"
            )
        )
    elif chk == False:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain(
                "Say Sorry I can't create the project problem occured or something like this"
            )
        )


def CreateFolder(reply):
    # Regular expression to find folderName and folderPath
    pattern = r"\{folderName=([^\}]+)\}|\{folderPath=([^\}]+)\}"

    # Find all matches
    matches = re.findall(pattern, reply)

    folderName = next((match[0] for match in matches if match[0]), None)
    folderPath = next((match[1] for match in matches if match[1]), None)

    print(f"Folder Name = {folderName}")
    print(f"Folder Path = {folderPath}")

    chk = System.CreateFolder(folderName=folderName, path=folderPath)
    if chk == True:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say Folder created or something like that")
        )
    elif chk == "FolderExist":
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say folder alreay exists or something like that")
        )
    elif chk == "PermissionError":
        esha.TextToSpeechWithPYttsx3(
            esha.Brain(
                "Say sorry I don't have proper permission or something like that"
            )
        )
    elif chk == False:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain(
                "Say oops something went wrong can't create the folder for now or something like that"
            )
        )


def OpenProj(reply):
    # Regular expression pattern to match projName and projPath
    pattern = r"\{projName=(\w+)\} \{projPath=([^\}]+)\}"  # Find the matches
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
            esha.TextToSpeechWithPYttsx3(
                esha.Brain("Say OOps Can't open the project or something like that")
            )
        else:
            esha.TextToSpeechWithPYttsx3(
                esha.Brain("Say Project Opened or Something like that")
            )
            data = []
            for f in files:
                iconPath = os.path.join("res", "file.png")
                dirPath = os.path.join(proj_path, proj_name)
                iconName = f
                d = {"iconName": iconName, "iconPath": iconPath, "dirPath": dirPath}
                data.append(d)
                print(f)
            for f in folders:
                dirPath = os.path.join(proj_path, proj_name)
                iconName = f
                iconPath = os.path.join("res", "folder.png")
                d = {"iconName": iconName, "iconPath": iconPath, "dirPath": dirPath}
                data.append(d)
                with open("icon.json", "a") as file:
                    json.dump(data, file, indent=4)
                
                print(data)
    else:
        print("No match found.")


def handle_interrupt(signal, frame):
    esha.ExitEsha()
    sys.exit(0)  # Exit the program gracefully


# Set up signal handler for Ctrl + C
signal.signal(signal.SIGINT, handle_interrupt)


def CallEsha():
    try:
        # print("\nListening......")
        # prompt = esha.SpeechToTextWithSpeech_recognition()
        prompt = input("\n>> ")
        # Only When Esha will be called if the user took her name
        # if "Esha" in prompt or "isha" in prompt:
        if prompt:
            reply = esha.Brain(prompt=prompt)
            # If it's a system message then Esha won't say it
            if "{system}" in reply:
                if "{CreateProject}" in reply:
                    CreateProject(reply)
                elif "{CreateFolder}" in reply:
                    CreateFolder(reply)
                elif "{OpenProj}" in reply:
                    OpenProj(reply)

            else:
                esha.TextToSpeechWithPYttsx3(reply)

    except Exception as e:
        print(f"[-]{e}")


if __name__=="__main__":
    try:
        while True:
            CallEsha();
    except KeyboardInterrupt:
       esha.Brain("Bye") 