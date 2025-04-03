import cv2
import mediapipe as mp
import time
import math

class HandTrackingDynamic:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.handsMp = mp.solutions.hands
        self.hands = self.handsMp.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.results = None
        self.lmsList = []
        self.handType = None  # To store hand type (left/right)

    def findFingers(self, frame, draw=True):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms, handedness in zip(self.results.multi_hand_landmarks, 
                                          self.results.multi_handedness):
                # Get hand type (left/right)
                self.handType = handedness.classification[0].label.lower()
                
                if draw:
                    self.mpDraw.draw_landmarks(
                        frame, handLms, self.handsMp.HAND_CONNECTIONS)
                    
        return frame

    def findPosition(self, frame, handNo=0, draw=True):
        xList, yList = [], []
        bbox = []
        self.lmsList = []
        
        if self.results and self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                handedness = self.results.multi_handedness[handNo]
                self.handType = handedness.classification[0].label.lower()

                for id, lm in enumerate(myHand.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    xList.append(cx)
                    yList.append(cy)
                    self.lmsList.append([id, cx, cy, self.handType])  # Store hand type with landmarks
                    if draw:
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bbox = xmin, ymin, xmax, ymax

                if draw:
                    cv2.rectangle(frame, (xmin - 20, ymin - 20), 
                                (xmax + 20, ymax + 20), (0, 255, 0), 2)

        return self.lmsList, bbox

    def findFingerUp(self):
        fingers = []
        if len(self.lmsList) == 0:
            return fingers

        # Thumb (uses hand type information)
        if (self.handType == "right" and self.lmsList[self.tipIds[0]][1] > self.lmsList[self.tipIds[0] - 1][1]) or \
           (self.handType == "left" and self.lmsList[self.tipIds[0]][1] < self.lmsList[self.tipIds[0] - 1][1]):
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        for id in range(1, 5):
            if self.lmsList[self.tipIds[id]][2] < self.lmsList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    # ... (rest of your methods remain the same)

def main():
    # ... (previous main code remains the same)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        frame = detector.findFingers(frame)
        
        # Process each hand separately
        totalFingers = 0
        for hand_num in range(2):  # Check up to 2 hands
            lmsList, bbox = detector.findPosition(frame, handNo=hand_num)
            if lmsList:
                fingers = detector.findFingerUp()
                totalFingers += sum(fingers)
        
        flipped = cv2.flip(frame, 1)
        cv2.putText(flipped, f'Fingers: {totalFingers}', (10, 30),
                   cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        # ... (rest of your display code)

if __name__ == "__main__":
    main()