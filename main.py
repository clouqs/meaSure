import cv2
import time
from hand_track import HandTrackingDynamic
from obj_dim import HandScaleMeasurement


def main():
    ptime = time.time()
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    measurement = HandScaleMeasurement(detector, ref_length_cm=18.0)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    # Settings
    show_landmarks = True
    freeze_frame = False
    frozen_frame = None
    frozen_measurements = None
    
    print("\n=== Hand Measurement System ===")
    print("Controls:")
    print("  Q - Quit")
    print("  M - Toggle measurement mode (bbox/fingertip)")
    print("  R - Recalibrate reference")
    print("  L - Toggle landmark visibility")
    print("  F - Freeze/unfreeze measurement")
    print("  S - Save screenshot")
    print("  C - Clear screen overlays")
    print("===============================\n")

    while True:
        if not freeze_frame:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break
            
            # Flip frame
            frame = cv2.flip(frame, 1)
            
            # Process hands
            frame = detector.findFingers(frame, draw=show_landmarks)
            lmsList, bbox = detector.findPosition(frame, draw=show_landmarks)
            totalFingers = detector.fingerCount(frame)
            
            # Measure
            frame, width, height = measurement.measure_object(frame)
            
            # Store for freeze
            frozen_frame = frame.copy()
            frozen_measurements = (width, height)
        else:
            frame = frozen_frame.copy()
            width, height = frozen_measurements
            
            # Add freeze indicator
            cv2.putText(frame, 'FROZEN', (frame.shape[1]//2 - 50, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # Display info
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        
        # Info panel with background
        info_height = 120
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (200, info_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        cv2.putText(frame, f'FPS: {int(fps)}', (5, 20),
                   cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
        cv2.putText(frame, f'Fingers: {totalFingers}', (5, 40), 
                   cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
        cv2.putText(frame, f'Width: {width:.1f}cm', (5, 60), 
                   cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
        if height > 0:
            cv2.putText(frame, f'Height: {height:.1f}cm', (5, 80), 
                       cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
        
        # Controls hint
        cv2.putText(frame, 'Press H for help', (5, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_PLAIN, 0.8, (150, 150, 150), 1)

        cv2.imshow('Hand Measurement System', frame)
        
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('m'):
            measurement.toggle_mode()
            print(f"Switched to {measurement.measurement_mode} mode")
        elif key == ord('r'):
            measurement.recalibrate()
            print("Recalibrating...")
        elif key == ord('l'):
            show_landmarks = not show_landmarks
            print(f"Landmarks: {'ON' if show_landmarks else 'OFF'}")
        elif key == ord('f'):
            freeze_frame = not freeze_frame
            print(f"Frame: {'FROZEN' if freeze_frame else 'LIVE'}")
        elif key == ord('s'):
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"measurement_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved: {filename}")
        elif key == ord('h'):   
            print("\n=== Controls ===")
            print("  Q - Quit")
            print("  M - Toggle measurement mode")
            print("  R - Recalibrate reference")
            print("  L - Toggle landmarks")
            print("  F - Freeze/unfreeze")
            print("  S - Save screenshot")
            print("  H - Show this help")
            print("================\n")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()