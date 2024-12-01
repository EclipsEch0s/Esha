import os
from pathlib import Path
import subprocess


class System:
    # For creating Folder
    @staticmethod
    def CreateFolder(path, folderName):
        try:
            os.mkdir(os.path.join(path, folderName))
            return True
        except FileExistsError:
            return "ProjExist"
        except PermissionError:
            return "PermissionError"
        except Exception:
            return False

    # For creating Files
    @staticmethod
    def CreateFile(path, fileName):
        filePath = os.path.join(path, fileName)
        if os.path.exists(filePath):
            return "FileExists"
        with open(filePath, "w"):
            return True

    # List Files and Folders in a Directory
    @staticmethod
    def ReturnFilesNFolderInAPath(path):
        try:
            filesNfolders = os.scandir(path)
        except Exception:
            return False, False
        files = []
        folders = []
        for fileNfolder in filesNfolders:
            if fileNfolder.is_file():
                files.append(fileNfolder.name)
            elif fileNfolder.is_dir():
                folders.append(fileNfolder.name)
        return files, folders

    @staticmethod
    def OpenApplication(applicationName):
        startMenu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        files, folder = System.ReturnFilesNFolderInAPath(startMenu) 
        for f in folder:
            if f == applicationName:
                path =os.path.join(startMenu, applicationName) 
                print(path) 
                fle, fold = System.ReturnFilesNFolderInAPath(path)
                print(applicationName+'.ink')
                for i in fle:
                    if i == (applicationName + '.lnk'):
                        appl = i
                        print(appl)
                        os.startfile(f"{os.path.join(path, appl)}")

