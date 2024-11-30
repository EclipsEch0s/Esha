import os


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
                files.append(fileNfolder)
            elif fileNfolder.is_dir():
                folders.append(fileNfolder)
        return files, folders
