import json
import re
from system import System

from esha import Esha


def CreateProject():
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
        # Adding the project details in project.json to keep a track of it
        with open("project.json") as file:
            data = json.load(file)
        data[projectName] = {"desc": projectDesc, "path": projectPath}
        with open("project.json", "w") as file:
            json.dump(data, file, indent=4)


        esha.TextToSpeechWithPYttsx3(
            esha.Brain(
                "Say Project created or something like that"
            )
        )
    elif chk == "FolderExist":
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

def CreateFolder():
    # Regex pattern to extract key-value pairs
    pattern = r"\{(\w+)=([^\}]+)\}"

    # Find all matches
    matches = re.findall(pattern, reply)

    # Create a dictionary from the matches
    project = {key: value for key, value in matches}

    # Access the project details
    folderName = project.get("folderName")
    folderPath = project.get("folderPath")

    print(f"Folder Name: {folderName}")
    print(f"Folder Path: {folderPath}") 

    chk = System.CreateFolder(folderName=folderName, path=folderPath)
    if chk == True:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say I created the folder for you or something like that")
        )
    elif chk == "FolderExist":
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say looks like the folder is already presented or something like that")
        )
    elif chk == "PermissionError":
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say I don't have proper permsion to create the folder or something like that")
        )
    elif chk == False:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say OOps something went wrong I couldn't create the folder or something like that")
        )

def GetProjDet():
    # Regex pattern to extract the value inside the parentheses
    pattern = r"\{GetProjDet\((\w+)\)\}"

    # Find the match
    match = re.search(pattern, reply)

    # Check if a match is found
    if match:
        detAbout = match.group(1)
        print(f"detAbout: {detAbout}")
        # Regex pattern to extract the value of 'name'
        pattern = r"\{name=([^\}]+)\}"

        # Find the match
        match = re.search(pattern, reply)

        # Check if a match is found
        if match:
            projName = match.group(1)
            print(f"Proj Name: {projName}")
        else:
            esha.Brain("Say no data found about the project or something like that")
        with open("project.json") as file:
            data = json.load(file)
            if detAbout == "desc":
                esha.TextToSpeechWithPYttsx3(
                    esha.Brain(
                        f"Say description of project is {data[projName]['desc']}"
                    )
                )
            elif detAbout == "path":
                esha.TextToSpeechWithPYttsx3(
                    esha.Brain(
                        f"Say location of project is {data[projName]['path']}"
                    )
                )
    else:
        esha.TextToSpeechWithPYttsx3(
            esha.Brain("Say no data found about the project or something like that")
        )


esha = Esha()
try:
    while True:
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
                        CreateProject()
                    if "{CreateFolder}" in reply:
                        CreateFolder()

                else:
                    esha.TextToSpeechWithPYttsx3(reply)

        except KeyboardInterrupt:
            reply = esha.Brain("Bye")
            esha.TextToSpeechWithPYttsx3(reply)
            exit()
        except Exception as e:
            print(f"[-]{e}")
except KeyboardInterrupt:
    reply = esha.Brain("Bye")
    esha.TextToSpeechWithPYttsx3(reply)
