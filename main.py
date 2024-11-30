import re
from system import System

from esha import Esha

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
                        # Regex pattern to extract key-value pairs
                        pattern = r"\{(\w+)=([^\}]+)\}"

                        # Find all matches
                        matches = re.findall(pattern, reply)

                        # Create a dictionary from the matches
                        projectDesc = {key: value for key, value in matches}

                        # Access the project details
                        projectName = projectDesc.get("projectName")
                        desc = projectDesc.get("desc")
                        projectPath = projectDesc.get("projectPath")

                        print(f"Project Name: {projectName}")
                        print(f"Description: {desc}")
                        print(f"Project Path: {projectPath}")
                        chk = System.CreateFolder(
                            folderName=projectName, path=projectPath
                        )
                        if chk == True:
                            esha.TextToSpeechWithPYttsx3(
                                esha.Brain(
                                    "Say Project created if you need any help please ask me or something like that"
                                )
                            )
                        elif chk == "ProjExist":
                            esha.TextToSpeechWithPYttsx3(
                                esha.Brain(
                                    "Say project already exist or something like that"
                                )
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
