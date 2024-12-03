import cv2
import mediapipe as mp
import pyautogui
import time

class HandTracker:
    def __init__(self, detectionConfidence=0.7, trackingConfidence=0.7):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            min_detection_confidence=detectionConfidence,
            min_tracking_confidence=trackingConfidence,
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.screenWidth, self.screenHeight = pyautogui.size()
        self.lastClickTime = 0
        self.startHoldTime = None
        self.doubleClickThreshold = 0.3  # Seconds between double clicks
        self.holdThreshold = 0.5  # Seconds for detecting a hold
        self.isThumbIndexTouching = False
        self.isHolding = False
        self.smoothFactor = 5

    def detectHandGestures(self, frame):
        """Detect hand gestures and move the cursor based on hand movement."""
        frameRgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRgb)

        if results.multi_hand_landmarks:
            for handLandmarks in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(frame, handLandmarks, self.mpHands.HAND_CONNECTIONS)

                # Get coordinates for index finger tip and thumb tip
                indexTip = handLandmarks.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
                thumbTip = handLandmarks.landmark[self.mpHands.HandLandmark.THUMB_TIP]

                # Map index finger position to screen
                screenX = self.screenWidth - int(indexTip.x * self.screenWidth)
                screenY = int(indexTip.y * self.screenHeight)

                # Smooth cursor movement
                currentMouseX, currentMouseY = pyautogui.position()
                smoothX = currentMouseX + (screenX - currentMouseX) // self.smoothFactor
                smoothY = currentMouseY + (screenY - currentMouseY) // self.smoothFactor

                # Move cursor
                pyautogui.moveTo(smoothX, smoothY)

                # Check if thumb and index finger are touching
                thumbIndexDistance = self.calculateDistance(indexTip, thumbTip)
                if thumbIndexDistance < 0.05:  # Adjust threshold for touch detection
                    self.handleClickAndHold()
                else:
                    self.resetHoldState()

        return frame

    def calculateDistance(self, point1, point2):
        """Calculate Euclidean distance between two normalized points."""
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

    def handleClickAndHold(self):
        """Handle single-click, double-click, and click-and-hold events."""
        currentTime = time.time()

        if not self.isThumbIndexTouching:
            self.isThumbIndexTouching = True
            self.startHoldTime = currentTime
            timeSinceLastClick = currentTime - self.lastClickTime

            if timeSinceLastClick < self.doubleClickThreshold:
                # Perform double-click
                pyautogui.doubleClick()
                print("Double Click")
            else:
                # Record the last click time for single-click detection
                self.lastClickTime = currentTime
        else:
            # If thumb and index are still touching, check for hold duration
            if self.startHoldTime and not self.isHolding:
                elapsedHoldTime = currentTime - self.startHoldTime
                if elapsedHoldTime >= self.holdThreshold:
                    self.isHolding = True
                    pyautogui.mouseDown()
                    print("Left Click and Hold")

    def resetHoldState(self):
        """Reset the hold state when thumb and index are no longer touching."""
        if self.isHolding:
            pyautogui.mouseUp()
            print("Released Hold")
        self.isThumbIndexTouching = False
        self.isHolding = False
        self.startHoldTime = None

    def run(self):
        """Run the hand tracking loop using the webcam."""
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame = self.detectHandGestures(frame)
            cv2.imshow("Hand Tracker", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                break

        cap.release()
        cv2.destroyAllWindows()
