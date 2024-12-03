from hand_tracking import HandTracker
import json
import tkinter as tk
from PIL import Image, ImageTk
from screeninfo import get_monitors
import os
import sys
import random
import threading  
from call_esha import CallEsha  

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.projector = self.GetMonitor(monitorId=0)
        self.projectorWidth, self.projectorHeight = self.projector.width, self.projector.height
        self.projectorX, self.projectorY = self.projector.x, self.projector.y
        self.root.title("E.S.H.A")
        
        # # Set the current project folder name
        # self.DisplayProjectFolder("xyz")

        # Configure full-screen mode
        # self.SetupFullscreen()

        # Load background and logo
        self.backgroundPath = os.path.join("res", "bgimg.jpg")
        self.CreateBackground(self.backgroundPath)
        
        self.logoPath = os.path.join("res", "ESHA_LOGO.png")
        self.CreateLogo(self.logoPath)

        # List to track icon positions (using a dict with unique ids)
        self.iconPositions = {}

        # List of icons Avaiable icons in screen with its path
        self.pathOfIconsInScreen = []

        # Start creating icons periodically
        self.create_icons_periodically()
        

        # Bind the Escape key to exit full-screen
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Bind the F11 key to toggle full-screen mode
        self.root.bind("<F11>", self.ToggleFullscreen)

        # Start the AI model in a separate thread
        self.run_esha_thread()

        self.RunHandTrackingThread()

    def create_icons_periodically(self):
        """Periodically call the CreateIcon function."""
       
        with open("icon.json") as file:
            try:
                data = json.load(file)
                for d in data:
                    icon_name = d['iconName']
                    icon_path = d['iconPath']
                    dir_path = d['dirPath']
                    iconAlreadyPresent = False
                    for i in self.pathOfIconsInScreen:
                        if i['iconName'] == icon_name:
                            iconAlreadyPresent = True
                    if not iconAlreadyPresent:
                        # Call the CreateIcon method
                        self.CreateIcon(icon_name, icon_path, dir_path)

            except:
                pass
            # Example icon data, replace with your actual data
        
        # Schedule this function to run again after 5000ms (5 seconds)
        self.root.after(200, self.create_icons_periodically)
    
    def GetMonitor(self, monitorId=1):
        """Retrieve the second monitor details."""
        monitors = get_monitors()
        if len(monitors) < 1:
            print("Error: A second screen (projector) is not detected.")
            sys.exit(1)
        return monitors[monitorId]

    def LoadImage(self, filePath, targetWidth=None, targetHeight=None):
        """Load and optionally resize an image, preserving transparency."""
        try:
            image = Image.open(filePath).convert("RGBA")  # Ensure image has an alpha channel (transparency)
            if targetWidth and targetHeight:
                image = image.resize((targetWidth, targetHeight), Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            print(f"Error loading image '{filePath}': {e}")
            sys.exit(1)

    def DarkenImage(self, image, opacity=0.8):
        """Apply a darkening overlay on the image."""
        overlay = Image.new("RGBA", image.size, (0, 0, 0, int(255 * opacity)))
        return Image.alpha_composite(image, overlay)

    def CreateBackground(self, imagePath, darkenOpacity=0.8):
        """Create and set the background image, with optional darkening."""
        bgImage = self.LoadImage(imagePath, self.projectorWidth, self.projectorHeight)
        darkenedBgImage = self.DarkenImage(bgImage, darkenOpacity)
        bgPhoto = ImageTk.PhotoImage(darkenedBgImage)
        
        backgroundLabel = tk.Label(self.root, image=bgPhoto)
        backgroundLabel.image = bgPhoto  # Store reference to image to prevent garbage collection
        backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)

    def CreateLogo(self, imagePath, maxLogoWidth=200):
        """Create and place the logo in the bottom right corner, preserving transparency."""
        logoImage = self.LoadImage(imagePath)
        logoWidth, logoHeight = logoImage.width, logoImage.height

        if logoWidth > maxLogoWidth:
            ratio = maxLogoWidth / logoWidth
            logoImage = self.LoadImage(imagePath, int(logoWidth * ratio), int(logoHeight * ratio))

        logoPhoto = ImageTk.PhotoImage(logoImage)
        
        # Place the logo in the bottom-right corner
        paddingX = 10
        paddingY = 10
        logoLabel = tk.Label(self.root, image=logoPhoto, bg="#000000")
        logoLabel.image = logoPhoto  # Store reference to image to prevent garbage collection
        logoLabel.place(
            x=self.projectorWidth - logoPhoto.width() - paddingX,
            y=self.projectorHeight - logoPhoto.height() - paddingY
        )

    def SetupFullscreen(self):
        """Configure the app for full-screen mode on a specific monitor."""
        self.root.geometry(f"{self.projectorWidth}x{self.projectorHeight}+{self.projectorX}+{self.projectorY}")
        self.root.overrideredirect(True)

    def ToggleFullscreen(self, event=None):
        """Toggle between full-screen and windowed mode."""
        if self.root.winfo_geom().startswith(str(self.projectorWidth)):
            self.root.geometry("800x600")  # Windowed mode, or set any desired window size
        else:
            self.SetupFullscreen()

    def DisplayProjectFolder(self, projectFolder):
        """Display the current project folder name at the top of the window."""
        folderLabel = tk.Label(self.root, 
                               text=f"Current Folder: {projectFolder}", 
                               font=("Arial", 18, "bold"),  # Slightly larger font size and bold
                               bg="#000000", 
                               fg="white", 
                               bd=0,  # Remove border
                               padx=10, pady=10)  # Optional padding to give space around text

        # Align the text to the center horizontally and place it at the top of the window
        folderLabel.place(relx=0.5, y=10, anchor="n")  # relx=0.5 centers horizontally, y=10 places it near top

        # Lift the folder label above all other elements to ensure visibility
        folderLabel.lift()

        # Ensure the text stays above other elements after everything is loaded
        self.root.after(0, folderLabel.lift)  # Force lift to run after everything is loaded

    def CreateIcon(self, iconName, iconPath, dirPath):
        # Create draggable icons with random placement and names
        pathOfIconInScreen = {"iconName":iconName, "dirPath":dirPath}
        self.pathOfIconsInScreen.append(pathOfIconInScreen)
        self.CreateDraggableIcon(iconPath, iconName)

    def CheckOverlap(self, xPos, yPos, iconWidth, iconHeight):
        """Check if the new icon overlaps with any existing icon."""
        for (existingX, existingY, existingWidth, existingHeight) in self.iconPositions.values():
            if (xPos < existingX + existingWidth and xPos + iconWidth > existingX and
                yPos < existingY + existingHeight and yPos + iconHeight > existingY):
                return True  # Overlap detected
        return False

    def CreateDraggableIcon(self, iconPath, iconName, width=50, height=50, maxOffset=200):
        """Create an icon on the screen with random placement, centered with some offset, and avoid overlap."""
        iconImage = self.LoadImage(iconPath, width, height)
        iconPhoto = ImageTk.PhotoImage(iconImage)
        
        # Find the center of the screen
        centerX = self.projectorWidth // 2
        centerY = self.projectorHeight // 2
        
        # Try to find a position that doesn't overlap with existing icons
        maxRetries = 100  # Max retries to find a non-overlapping position
        retries = 0
        while retries < maxRetries:
            # Randomly offset the icon from the center within a specified range (maxOffset)
            xPos = random.randint(centerX - maxOffset, centerX + maxOffset - width)
            yPos = random.randint(centerY - maxOffset, centerY + maxOffset - height)
            
            # Ensure icons don't go outside the screen boundaries
            xPos = max(0, min(self.projectorWidth - width, xPos))
            yPos = max(0, min(self.projectorHeight - height, yPos))
            
            # Check for overlap, if any, try again
            if not self.CheckOverlap(xPos, yPos, width, height):
                break
            retries += 1
        
        if retries == maxRetries:
            print("Warning: Couldn't find a non-overlapping position after several attempts.")

        iconLabel = tk.Label(self.root, image=iconPhoto, bg="#000000", bd=0)
        iconLabel.image = iconPhoto  # Store reference to image to prevent garbage collection
        iconLabel.place(x=xPos, y=yPos)
        
        nameLabel = tk.Label(self.root, text=iconName, bg="#000000", fg="white")
        nameLabel.place(x=xPos, y=yPos + height)

        # Assign a unique ID to each icon for easier tracking
        iconId = len(self.iconPositions) + 1
        self.iconPositions[iconId] = (xPos, yPos, width, height)

        # Make the icon draggable with its name
        DraggableIcon(iconLabel, nameLabel, self, iconId)

    def run_esha_thread(self):
        """Start a separate thread for the CallEsha function to run concurrently."""
        def esha_loop():
            # Call the AI function, and then schedule it to run periodically
            CallEsha()
            self.root.after(1000, esha_loop)  # Call again after 1 second (you can adjust this interval)

        threading.Thread(target=esha_loop, daemon=True).start()
   
    def RunHandTrackingThread(self):
        """Start a separate thread for the hand tracking function."""
        def handTrackingLoop():
            tracker = HandTracker()
            tracker.run()  # Start hand tracking and mouse control in the same loop

        threading.Thread(target=handTrackingLoop, daemon=True).start()


    def Run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()


class DraggableIcon:
    def __init__(self, iconLabel, nameLabel, app, iconId):
        self.iconLabel = iconLabel
        self.nameLabel = nameLabel
        self.app = app
        self.iconId = iconId
        self.iconLabel._drag_data = None
        self.iconLabel.bind("<ButtonPress-1>", self.OnPress)
        self.iconLabel.bind("<B1-Motion>", self.OnDrag)
        self.iconLabel.bind("<ButtonRelease-1>", self.OnRelease)

    def OnPress(self, event):
        """Store the initial position when the mouse button is pressed."""
        self.iconLabel._drag_data = {'x': event.x, 'y': event.y}

    def OnDrag(self, event):
        """Update the position of the icon and its name as it is dragged.""" 
        dx = event.x - self.iconLabel._drag_data['x']
        dy = event.y - self.iconLabel._drag_data['y']
        self.iconLabel.place(x=self.iconLabel.winfo_x() + dx, y=self.iconLabel.winfo_y() + dy)
        self.nameLabel.place(x=self.iconLabel.winfo_x(), y=self.iconLabel.winfo_y() + self.iconLabel.winfo_height())

    def OnRelease(self, event):
        """Update the icon's position after it has been released.""" 
        newX = self.iconLabel.winfo_x()
        newY = self.iconLabel.winfo_y()
        width = self.iconLabel.winfo_width()
        height = self.iconLabel.winfo_height()

        # Update the position in the app's iconPositions dictionary
        self.app.iconPositions[self.iconId] = (newX, newY, width, height)

# Run the app
if __name__ == "__main__":
    app = App()
    app.Run()
