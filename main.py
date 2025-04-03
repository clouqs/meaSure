import cv2
import os 
import mediapipe as mp

self.handsMP = mp.solutions.hands #Mp.solution.hands module performs the hand recognition algorithm. So, we create the object and store it in mpHands.
self.hands = self.handsMP.Hands() # Using mpHands.Hands method we configured the model. The first argument is max_num_hands, that means the maximum number of hands will be detected by the model in a single frame. MediaPipe can detect multiple hands in a single frame, but we’ll detect only one hand at a time in this project.
self.mpDraw = mp.solutions.drawing_utils #Mp.solutions.drawing_utils will draw the detected key points for us so that we don’t have to draw them manually.



