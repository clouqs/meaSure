import cv2
import mediapipe as mp
import time
import math


# obj_dim.py
class HandScaleMeasurement:
    def __init__(self, detector, ref_length_cm=18.0):  # Add detector parameter
        self.detector = detector  # Use the passed detector
        self.ref_length_cm = ref_length_cm
        self.ref_length_px = None

    def get_reference_scale(self, left_hand_landmarks, frame_shape):
        """Calculate pixel length from middle finger tip (12) to wrist (0)"""
        h, w = frame_shape[:2]
        
        # Middle finger tip to wrist
        x1, y1 = left_hand_landmarks.landmark[12].x * w, left_hand_landmarks.landmark[12].y * h
        x2, y2 = left_hand_landmarks.landmark[0].x * w, left_hand_landmarks.landmark[0].y * h
        
        self.ref_length_px = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return self.ref_length_px

    def measure_object(self, frame):
        if not hasattr(self.detector, 'results') or not self.detector.results.multi_hand_landmarks:
            return frame, 0, 0

        h, w = frame.shape[:2]
        hands = self.detector.results.multi_hand_landmarks
        
        # Need exactly 2 hands for measurement
        if len(hands) != 2:
            return frame, 0, 0

        # Identify left/right hands (left hand is on left side of frame)
        if hands[0].landmark[0].x < hands[1].landmark[0].x:
            left_hand, right_hand = hands[0], hands[1]
        else:
            left_hand, right_hand = hands[1], hands[0]

        # Calculate reference scale
        self.get_reference_scale(left_hand, frame.shape)
        if not self.ref_length_px:
            return frame, 0, 0

        cm_per_pixel = self.ref_length_cm / self.ref_length_px

        # Measure object in right hand
        right_landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in right_hand.landmark]
        x_coords, y_coords = zip(*right_landmarks)
        
        xmin, xmax = min(x_coords), max(x_coords)
        ymin, ymax = min(y_coords), max(y_coords)

        # Calculate dimensions
        width_px = xmax - xmin
        height_px = ymax - ymin
        width_cm = width_px * cm_per_pixel
        height_cm = height_px * cm_per_pixel

        # Visualization
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(frame, f'{width_cm:.1f}x{height_cm:.1f} cm', 
                   (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        
        # Draw reference line
        left_tip = (int(left_hand.landmark[12].x * w), int(left_hand.landmark[12].y * h))
        left_wrist = (int(left_hand.landmark[0].x * w), int(left_hand.landmark[0].y * h))
        cv2.line(frame, left_tip, left_wrist, (0, 0, 255), 2)
        cv2.putText(frame, f'Reference: {self.ref_length_cm}cm', 
                   (left_wrist[0]-50, left_wrist[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

        return frame, width_cm, height_cm