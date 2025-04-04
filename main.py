import cv2
import time
import math
import mediapipe as mp # type: ignore
from hand_track import *
from obj_dim import *




def main():
    ptime = time.time()
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    measurement = HandScaleMeasurement(detector, ref_length_cm=18.0)  # Pass the detector
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        

        #frame flip
        frame = cv2.flip(frame, 1)

        frame = detector.findFingers(frame)
        lmsList, bbox = detector.findPosition(frame)
        totalFingers = detector.fingerCount(frame)
        
        frame, width, height = measurement.measure_object(frame)

        # Display info
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        
        cv2.putText(frame, f'FPS: {int(fps)}', (5, 40),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)
        cv2.putText(frame, f'Fingers: {totalFingers}', (5, 20), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)      
        cv2.putText(frame, f'Q = Quit', (5, 60), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

        cv2.imshow('Hand Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()