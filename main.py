import cv2
import time
import math
import mediapipe as mp
from hand_track import HandTrackingDynamic
from obj_dim import HandScaleMeasurement




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

        frame = detector.findFingers(frame)
        lmsList, bbox = detector.findPosition(frame)
        totalFingers = detector.fingerCount(frame)
        
        # Add measurement
        frame, width, height = measurement.measure_object(frame)

        flipped = cv2.flip(frame, 1)

        # Display info
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        
        cv2.putText(flipped, f'FPS: {int(fps)}', (10, 40),
                   cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)
        cv2.putText(flipped, f'Fingers: {totalFingers}', (10, 20), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
        
        # Show measurements if valid
        if width > 0 and height > 0:
            cv2.putText(flipped, f'Size: {width:.1f}x{height:.1f}cm', (10, 60), 
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
        
        cv2.putText(flipped, f'Q = Quit', (10, 80), 
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

        cv2.imshow('Hand Tracking', flipped)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()