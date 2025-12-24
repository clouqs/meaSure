import cv2
<<<<<<< HEAD
import mediapipe as mp # type: ignore
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
        
        x1, y1 = left_hand_landmarks.landmark[12].x * w, left_hand_landmarks.landmark[12].y * h
        x2, y2 = left_hand_landmarks.landmark[0].x * w, left_hand_landmarks.landmark[0].y * h
        
        self.ref_length_px = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return self.ref_length_px

=======
import mediapipe as mp
import numpy as np
from collections import deque
import math


class HandScaleMeasurement:
    def __init__(self, detector, ref_length_cm=18.0):
        self.detector = detector
        self.ref_length_cm = ref_length_cm
        self.ref_length_px = None
        
        # Temporal smoothing
        self.measurement_buffer = deque(maxlen=10)
        self.scale_buffer = deque(maxlen=15)
        
        # Calibration
        self.calibrated = False
        self.calibration_samples = []
        self.calibration_needed = 30
        
        # Measurement modes
        self.measurement_mode = 'bbox'  # 'bbox', 'fingertip', 'custom'
        self.custom_points = []
        
        # Distance tracking
        self.stable_frames = 0
        self.stability_threshold = 5
        
    def calibrate_reference(self, left_hand_landmarks, frame_shape):
        """Multi-frame calibration for more accurate reference"""
        h, w = frame_shape[:2]
        
        x1 = left_hand_landmarks.landmark[12].x * w
        y1 = left_hand_landmarks.landmark[12].y * h
        x2 = left_hand_landmarks.landmark[0].x * w
        y2 = left_hand_landmarks.landmark[0].y * h
        
        ref_length = math.hypot(x2 - x1, y2 - y1)
        
        self.calibration_samples.append(ref_length)
        
        if len(self.calibration_samples) >= self.calibration_needed:
            # Remove outliers using IQR method
            samples = np.array(self.calibration_samples)
            q1, q3 = np.percentile(samples, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered = samples[(samples >= lower_bound) & (samples <= upper_bound)]
            
            self.ref_length_px = np.median(filtered)
            self.calibrated = True
            return True
        return False
    
    def get_reference_scale(self, left_hand_landmarks, frame_shape):
        """Calculate pixel length with temporal smoothing"""
        h, w = frame_shape[:2]
        
        x1 = left_hand_landmarks.landmark[12].x * w
        y1 = left_hand_landmarks.landmark[12].y * h
        x2 = left_hand_landmarks.landmark[0].x * w
        y2 = left_hand_landmarks.landmark[0].y * h
        
        ref_length = math.hypot(x2 - x1, y2 - y1)
        
        # Temporal smoothing
        self.scale_buffer.append(ref_length)
        self.ref_length_px = np.median(self.scale_buffer)
        
        return self.ref_length_px
    
    def measure_with_fingertips(self, right_hand, frame_shape):
        """Measure using two specific fingertips (thumb and index)"""
        h, w = frame_shape[:2]
        
        # Thumb tip (4) and index tip (8)
        x1 = int(right_hand.landmark[4].x * w)
        y1 = int(right_hand.landmark[4].y * h)
        x2 = int(right_hand.landmark[8].x * w)
        y2 = int(right_hand.landmark[8].y * h)
        
        distance_px = math.hypot(x2 - x1, y2 - y1)
        
        return distance_px, (x1, y1), (x2, y2)
    
    def measure_hand_dimensions(self, right_hand, frame_shape):
        """Comprehensive hand measurements"""
        h, w = frame_shape[:2]
        
        measurements = {}
        
        # Palm width (base of index to base of pinky)
        palm_x1 = int(right_hand.landmark[5].x * w)
        palm_y1 = int(right_hand.landmark[5].y * h)
        palm_x2 = int(right_hand.landmark[17].x * w)
        palm_y2 = int(right_hand.landmark[17].y * h)
        measurements['palm_width'] = math.hypot(palm_x2 - palm_x1, palm_y2 - palm_y1)
        
        # Individual finger lengths
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        base_ids = [1, 5, 9, 13, 17]
        tip_ids = [4, 8, 12, 16, 20]
        
        for name, base_id, tip_id in zip(finger_names, base_ids, tip_ids):
            bx = int(right_hand.landmark[base_id].x * w)
            by = int(right_hand.landmark[base_id].y * h)
            tx = int(right_hand.landmark[tip_id].x * w)
            ty = int(right_hand.landmark[tip_id].y * h)
            measurements[f'{name}_length'] = math.hypot(tx - bx, ty - by)
        
        return measurements
    
    def check_stability(self, current_measurement):
        """Check if measurements are stable"""
        if len(self.measurement_buffer) < 5:
            return False
        
        recent = list(self.measurement_buffer)[-5:]
        std_dev = np.std(recent)
        
        return std_dev < 0.5  # Less than 0.5cm variation
    
>>>>>>> cde5c0a (Enhanced hand measurement system with calibration and multiple modes)
    def measure_object(self, frame):
        if not hasattr(self.detector, 'results') or not self.detector.results.multi_hand_landmarks:
            return frame, 0, 0

        h, w = frame.shape[:2]
<<<<<<< HEAD
        hands = self.detector.results.multi_hand_landmarks       
        if len(hands) != 2:
            return frame, 0, 0

        # Identify hands (left is hand with smaller x-coordinate at wrist)
=======
        hands = self.detector.results.multi_hand_landmarks
        
        if len(hands) != 2:
            cv2.putText(frame, 'Show both hands!', (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame, 0, 0

        # Identify hands by wrist position
>>>>>>> cde5c0a (Enhanced hand measurement system with calibration and multiple modes)
        if hands[0].landmark[0].x < hands[1].landmark[0].x:
            left_hand, right_hand = hands[0], hands[1]
        else:
            left_hand, right_hand = hands[1], hands[0]

<<<<<<< HEAD
        # Get reference scale
=======
        # Calibration phase
        if not self.calibrated:
            is_calibrated = self.calibrate_reference(left_hand, (h, w))
            progress = len(self.calibration_samples) / self.calibration_needed
            
            cv2.putText(frame, f'Calibrating: {int(progress*100)}%', (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(frame, 'Keep left hand steady!', (10, 140),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Draw calibration indicator
            cv2.rectangle(frame, (10, 160), (10 + int(600 * progress), 180), 
                         (0, 255, 0), -1)
            
            if is_calibrated:
                cv2.putText(frame, 'Calibration Complete!', (10, 220),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return frame, 0, 0

        # Get reference scale with smoothing
>>>>>>> cde5c0a (Enhanced hand measurement system with calibration and multiple modes)
        self.get_reference_scale(left_hand, (h, w))
        if not self.ref_length_px:
            return frame, 0, 0

        cm_per_pixel = self.ref_length_cm / self.ref_length_px

<<<<<<< HEAD
        fingertip_ids = [0, 4, 8, 12, 16, 20]
        right_landmarks = [(int(right_hand.landmark[i].x * w), int(right_hand.landmark[i].y * h)) for i in fingertip_ids]
        x_coords, y_coords = zip(*right_landmarks)
        xmin, xmax = min(x_coords), max(x_coords)
        ymin, ymax = min(y_coords), max(y_coords)

        width_px = xmax - xmin
        height_px = ymax - ymin
        width_cm = width_px * cm_per_pixel
        height_cm = height_px * cm_per_pixel   

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        
        left_tip = (int(left_hand.landmark[12].x * w), int(left_hand.landmark[12].y * h))
        left_wrist = (int(left_hand.landmark[0].x * w), int(left_hand.landmark[0].y * h))
        cv2.line(frame, left_tip, left_wrist, (0, 0, 255), 2)
        
        cv2.putText(frame, f'{width_cm:.1f}x{height_cm:.1f} cm', 
                (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        cv2.putText(frame, f'Reference: {self.ref_length_cm}cm', 
                (left_wrist[0]-50, left_wrist[1]+30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        
        return frame, width_cm, height_cm
=======
        # Different measurement modes
        if self.measurement_mode == 'bbox':
            # Bounding box mode (original)
            fingertip_ids = [0, 4, 8, 12, 16, 20]
            right_landmarks = [(int(right_hand.landmark[i].x * w), 
                              int(right_hand.landmark[i].y * h)) for i in fingertip_ids]
            x_coords, y_coords = zip(*right_landmarks)
            xmin, xmax = min(x_coords), max(x_coords)
            ymin, ymax = min(y_coords), max(y_coords)

            width_px = xmax - xmin
            height_px = ymax - ymin
            
        elif self.measurement_mode == 'fingertip':
            # Fingertip distance mode
            distance_px, pt1, pt2 = self.measure_with_fingertips(right_hand, (h, w))
            width_px = distance_px
            height_px = 0
            xmin, ymin = pt1
            xmax, ymax = pt2
            
            # Draw measurement line
            cv2.line(frame, pt1, pt2, (255, 0, 255), 3)
            cv2.circle(frame, pt1, 8, (255, 0, 0), -1)
            cv2.circle(frame, pt2, 8, (0, 255, 0), -1)

        # Convert to cm with smoothing
        width_cm = width_px * cm_per_pixel
        height_cm = height_px * cm_per_pixel
        
        self.measurement_buffer.append(width_cm)
        smoothed_width = np.median(self.measurement_buffer)
        
        # Check stability
        is_stable = self.check_stability(smoothed_width)
        
        # Visualizations
        if self.measurement_mode == 'bbox':
            color = (0, 255, 0) if is_stable else (0, 165, 255)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            
            if height_cm > 0:
                cv2.putText(frame, f'{smoothed_width:.1f}x{height_cm:.1f} cm', 
                           (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            else:
                cv2.putText(frame, f'{smoothed_width:.1f} cm', 
                           (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        
        elif self.measurement_mode == 'fingertip':
            cv2.putText(frame, f'{smoothed_width:.1f} cm', 
                       ((xmin+xmax)//2, (ymin+ymax)//2 - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,255), 2)
        
        # Reference line
        left_tip = (int(left_hand.landmark[12].x * w), int(left_hand.landmark[12].y * h))
        left_wrist = (int(left_hand.landmark[0].x * w), int(left_hand.landmark[0].y * h))
        cv2.line(frame, left_tip, left_wrist, (0, 0, 255), 2)
        cv2.circle(frame, left_tip, 5, (0, 255, 255), -1)
        cv2.circle(frame, left_wrist, 5, (0, 255, 255), -1)
        
        # Info panel
        cv2.putText(frame, f'Reference: {self.ref_length_cm}cm', 
                   (left_wrist[0]-50, left_wrist[1]+30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        
        stability_text = 'STABLE' if is_stable else 'STABILIZING...'
        stability_color = (0, 255, 0) if is_stable else (0, 165, 255)
        cv2.putText(frame, stability_text, (10, h-20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, stability_color, 2)
        
        # Mode indicator
        cv2.putText(frame, f'Mode: {self.measurement_mode.upper()}', (10, h-50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Comprehensive measurements
        hand_measurements = self.measure_hand_dimensions(right_hand, (h, w))
        y_offset = 100
        for name, px_value in hand_measurements.items():
            cm_value = px_value * cm_per_pixel
            display_name = name.replace('_', ' ').title()
            cv2.putText(frame, f'{display_name}: {cm_value:.1f}cm', 
                       (w-250, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.4, (200, 200, 200), 1)
            y_offset += 20
        
        return frame, smoothed_width, height_cm
    
    def toggle_mode(self):
        """Switch between measurement modes"""
        modes = ['bbox', 'fingertip']
        current_idx = modes.index(self.measurement_mode)
        self.measurement_mode = modes[(current_idx + 1) % len(modes)]
        self.measurement_buffer.clear()
    
    def recalibrate(self):
        """Reset calibration"""
        self.calibrated = False
        self.calibration_samples = []
        self.measurement_buffer.clear()
        self.scale_buffer.clear()
>>>>>>> cde5c0a (Enhanced hand measurement system with calibration and multiple modes)
