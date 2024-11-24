import os
class Esha():
    def Greet(self):
        print("Welcome RK!")

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
