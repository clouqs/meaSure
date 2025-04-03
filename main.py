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
        self.lmsList = []  # Clear the list for new frame
        self.handTypes = []  # Store hand types separately

        if self.results and self.results.multi_hand_landmarks:
            for handNo, (handLms, handedness) in enumerate(zip(self.results.multi_hand_landmarks, 
                                                            self.results.multi_handedness)):
                handType = handedness.classification[0].label.lower()
                self.handTypes.append(handType)
                
                singleHandLms = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    singleHandLms.append([id, cx, cy, handType])
                    
                    if draw:
                        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), cv2.FILLED)
                
                self.lmsList.append(singleHandLms)  # Keep landmarks separated by hand

                if draw:
                    # Draw connections for each finger
                    connections = self.handsMp.HAND_CONNECTIONS
                    for connection in connections:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        cv2.line(frame, 
                                (singleHandLms[start_idx][1], singleHandLms[start_idx][2]),
                                (singleHandLms[end_idx][1], singleHandLms[end_idx][2]),
                                (26, 232, 204), 2)

        return self.lmsList, bbox
    
    def findFingerUp(self):
        fingers = []
        if not self.results or not self.results.multi_hand_landmarks:
            return fingers
        for hand_idx, handLms in enumerate(self.results.multi_hand_landmarks):
            handType = self.handTypes[hand_idx]
            handLms = self.lmsList[hand_idx]
            handFingers = []

            # Thumb (check x position for left/right hand)
            if handType == "right":
                handFingers.append(1 if handLms[self.tipIds[0]][1] < handLms[self.tipIds[0]-1][1] else 0)
            else:
                handFingers.append(1 if handLms[self.tipIds[0]][1] > handLms[self.tipIds[0]-1][1] else 0)

            # Other fingers (check y position)
            for id in range(1, 5):
                handFingers.append(1 if handLms[self.tipIds[id]][2] < handLms[self.tipIds[id]-2][2] else 0)

            fingers.append(handFingers)  # Keep fingers separated by hand

        return fingers

    def fingerCount(self, frame):
        fingers = self.findFingerUp()
        totalFingers = sum([sum(hand) for hand in fingers])  # Sum fingers per hand, then sum totals
        return min(totalFingers, 10)  # Cap at 10 fingers

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

def main():
    ptime = time.time()
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

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
        cv2.putText(flipped,f'FPS: {int(fps)}', (10, 40),
                   cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)

        cv2.putText(flipped, f'Fingers: {totalFingers}', (10, 20), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)

        cv2.imshow('Hand Tracking', flipped)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
