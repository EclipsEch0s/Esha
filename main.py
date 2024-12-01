import json
import re
from system import System
import signal
import sys

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
        esha.TextToSpeechWithPYttsx3(
            esha.Brain(
                "Say Project created or something like that"
            )
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



esha = Esha()

def handle_interrupt(signal, frame):
    esha.ExitEsha()
    sys.exit(0)  # Exit the program gracefully

# Set up signal handler for Ctrl + C
signal.signal(signal.SIGINT, handle_interrupt)

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

            else:
                esha.TextToSpeechWithPYttsx3(reply)

    except Exception as e:
        print(f"[-]{e}")

