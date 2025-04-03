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
        self.hands = self.handsMp.Hands(static_image_mode=self.mode, 
                                        max_num_hands=self.maxHands, 
                                        min_detection_confidence=self.detectionCon, 
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.results = None
        self.lmsList = []

    def findFingers(self, frame, draw=True):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)  

        if self.results.multi_hand_landmarks:
            for handLms, handedness in zip(self.results.multi_hand_landmarks, self.results.multi_handedness):
                self.handType = handedness.classification[0].label.lower()

        return frame

    def findPosition(self, frame, draw=True):
        xList, yList = [], []
        bbox = []
        self.lmsList = []

        if self.results and self.results.multi_hand_landmarks:
            for handNo, handLms in enumerate(self.results.multi_hand_landmarks):
                xList.clear()
                yList.clear()
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    xList.append(cx)
                    yList.append(cy)
                    self.lmsList.append([id, cx, cy, self.handType])

                    # Draw circle at each landmark point
                    if draw:
                        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), cv2.FILLED)

                # Draw lines between landmarks within the same finger
                if draw:
                    # Connect the finger landmarks (e.g., thumb -> index -> middle -> ring -> pinky)
                    for finger in [[0, 1, 2, 3, 4],  # Thumb
                                [5, 6, 7, 8],     # Index
                                [9, 10, 11, 12],  # Middle
                                [13, 14, 15, 16], # Ring
                                [17, 18, 19, 20]]: # Pinky
                        for i in range(1, len(finger)):  # Start from the second landmark in each finger
                            cv2.line(frame, (xList[finger[i-1]], yList[finger[i-1]]),
                                    (xList[finger[i]], yList[finger[i]]), (26, 232, 204), 2)   #BGR format

                    # Draw lines between palm landmarks (e.g., between base of fingers and wrist)
                    palm_base = [5, 9, 13, 17]  # Base of each finger
                    wrist = 0  # Wrist landmark (this is typically landmark 0, but can vary)
                    for i in range(1, len(palm_base)):
                        cv2.line(frame, (xList[palm_base[i-1]], yList[palm_base[i-1]]),
                                (xList[palm_base[i]], yList[palm_base[i]]), (26, 232, 204), 2)  #yellow lines

                    # Connect wrist to base of all fingers

                    #if draw:
                        #for i in range(5):
                            #cv2.line(frame, (xList[wrist], yList[wrist]), 
                                    #(xList[palm_base[i]], yList[palm_base[i]]), (255, 255, 0), 2)

                # Draw bounding box around the hand

                #xmin, xmax = min(xList), max(xList)
                #ymin, ymax = min(yList), max(yList)
                #bbox = xmin, ymin, xmax, ymax
                #if draw:
                    #cv2.rectangle(frame, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)

        return self.lmsList, bbox




    def findFingerUp(self):
        fingers = []

        if len(self.lmsList) == 0:
            return fingers  # Return an empty list if no landmarks are detected

        # Loop through all the hands
        for handNo, handLms in enumerate(self.results.multi_hand_landmarks):
            # Determine if it's a left or right hand based on thumb and pinky positions
            handType = "right" if handLms.landmark[self.tipIds[0]].x < handLms.landmark[self.tipIds[4]].x else "left"

            # Thumb (different check for right/left hand)
            if (handType == "right" and self.lmsList[self.tipIds[0]][1] > self.lmsList[self.tipIds[0] - 1][1]) or \
            (handType == "left" and self.lmsList[self.tipIds[0]][1] < self.lmsList[self.tipIds[0] - 1][1]):
                fingers.append(1)
            else:
                fingers.append(0)

            # Other fingers (same for both hands)
            for id in range(1, 5):
                if self.lmsList[self.tipIds[id]][2] < self.lmsList[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

        return fingers



    def findDistance(self, p1, p2, frame, draw=True, r=15, t=3):
        if len(self.lmsList) == 0:
            return None, frame, []

        x1, y1 = self.lmsList[p1][1:]
        x2, y2 = self.lmsList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(frame, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), r, (255, 0, 0), cv2.FILLED)
            cv2.circle(frame, (cx, cy), r, (0, 255, 0), cv2.FILLED)
        
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance, frame, [x1, y1, x2, y2, cx, cy]
    
    def fingerCount(self, frame):
        fingers = self.findFingerUp()
        totalFingers = sum(fingers)
        if totalFingers == 6:     #weird error handling
            totalFingers = 5      #weird that it counts 6 fingers
        elif totalFingers == 0:   #will fix later (messo una pezza)
            totalFingers = 0
        else:
            totalFingers = totalFingers + 1
        return totalFingers   #count fingers - needs better logic
def main():
    ptime = time.time()
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        frame = detector.findFingers(frame)
        lmsList, bbox = detector.findPosition(frame)

        totalFingers = detector.fingerCount(frame)

        flipped = cv2.flip(frame, 1)

        # Calculate and display FPS
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        cv2.putText(flipped,f'FPS: {int(fps)}', (10, 50), 
                   cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)

        cv2.putText(flipped, f'Fingers: {totalFingers}', (10, 30), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)

        cv2.imshow('Hand Tracking', flipped)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
