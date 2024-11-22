import cv2
import mediapipe as mp

# Test
class HandTrack:
    # Initialising Vars
    def __init__(self, camID=0, frameHeight=600, frameWidht=600) -> None:
        self.cap = cv2.VideoCapture(camID)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frameHeight)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frameWidht)
        self.mpDrawing = mp.solutions.drawing_utils
        self.mpDrawingStyle = mp.solutions.drawing_styles
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()

    # HandTracking for a frame only
    def HandTrack(self):
        self.data, self.image = self.cap.read()
        self.image = cv2.cvtColor(cv2.flip(self.image, 1), cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(self.image)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        if self.results.multi_hand_landmarks:
            for handLandmark in self.results.multi_hand_landmarks:
                self.mpDrawing.draw_landmarks(
                    self.image, handLandmark, self.mpHands.HAND_CONNECTIONS
                )
        cv2.imshow("HoloMat", self.image)
        cv2.waitKey(1)