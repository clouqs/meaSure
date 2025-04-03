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
                        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

                # Draw lines between all consecutive landmarks
                if draw:
                    for i in range(1, len(handLms.landmark)):  # Start from the second landmark
                        # Connect each landmark to the previous one
                        cv2.line(frame, (xList[i-1], yList[i-1]), (xList[i], yList[i]), (255, 255, 0), 2)

                # Draw bounding box around the hand
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bbox = xmin, ymin, xmax, ymax
                if draw:
                    cv2.rectangle(frame, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)

        return self.lmsList, bbox