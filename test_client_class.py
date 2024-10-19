import mediapipe as mp
import cv2
import numpy as np

from process_cursor import *
from datetime import datetime
from gesture_processing import *

##04/16 추가
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from OneEuroFilter import *
from paintscreen import *

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

##gesture recognizer 의 출력함수, option 초기화시 사용
class Callback_handler:
    def __init__(self):
        self.gesture = None

    def print_result(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        self.gesture = result.gestures
'''
------------------------------------
'''
class HandGesture:
    def __init__(self,LT,RB,CamRes_x,CamRes_y,monitor_width=1920,monitor_height=1080):
        self.lstm_gesture = '?'##학습한 LSTM 모델이 추론한 제스처
        self.recognizer_gesture = '?' ##gesture recognizer가 추론한 제스처
        self.event_gesture = '?'
        self.mediapipe_gesture = Callback_handler()
        self.Res_Con=ResContainer(LT,RB,CamRes_x,CamRes_y,monitor_width,monitor_height)     
        ##해상도 정보를 저장하는 컨테이너, 감지 해상도, 카메라 해상도, 모니터 해상도를 저장함.
        self.M_Info=MouseInfo(3,mouse.Controller())     ##커서 핸들 클래스 정의. 컨트롤러도 여기로 보냄
    ##액션 처리
    def mouse_events_handler(self, index_finger):#index_finger mediapipe hands landmark의 5번의 y좌표임.
        self.M_Info.Refresh_Mouse_Pos(index_finger,self.Res_Con,self.event_gesture)

    def main(self):
        try:
            #gesture_recognizer 관련 초기화
            options = GestureRecognizerOptions(
                base_options=BaseOptions(model_asset_path='./ttttt/gesture_recognizer.task'),
                running_mode=VisionRunningMode.LIVE_STREAM,
                result_callback=self.mediapipe_gesture.print_result)
            recognizer=GestureRecognizer.create_from_options(options)

            #hands 관련 초기화
            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.8,
                min_tracking_confidence=0.8)
            
            mp_drawing = mp.solutions.drawing_utils

            cap = cv2.VideoCapture(0)
            timestamp = 0

            config = {
                'freq': 30,
                'mincutoff': 30.0, 
                'beta': 3.0,      
                'dcutoff': 50.0    
            }
            
            while cap.isOpened():
                ##영상 전처리
                ret, frame = cap.read()
                if not ret:
                    print("Error: Cam Error")
                    break
                frame = cv2.flip(frame,1)
                img = cv2.resize(frame, (self.Res_Con.CamRes_x, self.Res_Con.CamRes_y))
                cv2.rectangle(img, (self.Res_Con.LT_x,self.Res_Con.LT_y), (self.Res_Con.RB_x,self.Res_Con.RB_y), (0,255,0) , 1)##인식범위 출력

                result = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))# 손 인식을 위해 BGR을 RGB로 변환 
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
                
                timestamp += 1
                recognizer.recognize_async(mp_img, timestamp)

                if result.multi_hand_landmarks is not None:#손을 인식했을때 랜드마 출력 및 joint_data에 저장.
                    if(len(self.mediapipe_gesture.gesture) != 0):
                       self.recognizer_gesture = self.mediapipe_gesture.gesture[0][0].category_name
                    joint_data = np.zeros((21, 4))
                    hand_filter = OneEuroFilter(**config)
                    for res in result.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)
                        for j, lm in enumerate(res.landmark):
                            filtered_x = hand_filter(lm.x)
                            filtered_y = hand_filter(lm.y)
                            joint_data[j] = [filtered_x, filtered_y, lm.z, lm.visibility]

        
                    self.lstm_gesture = gesture_recognition_lstm(joint_data)##인식된 손 처리
                    self.event_gesture = gesture_event(self.lstm_gesture,self.recognizer_gesture)
                    self.mouse_events_handler(joint_data[0])##마우스 이벤트 처리,
                    ##어차피 하나의 포인터에 대해서만 처리를해서 랜드마크 모든 점을 넘겨줄 필요는 없을거같습니다.
                    ##이제 그냥 0번째 좌표로 이벤트 처리하는걸로 하겠습니다.

                    img = cv2.putText(img, self.event_gesture, (50,50), cv2.FONT_HERSHEY_SIMPLEX ,  
                        1, (0,0,0), 2, cv2.LINE_AA)

                cv2.imshow('TouchFree', img)
                if cv2.waitKey(1) == ord('q'): #캠 화면 누르고 q누르면 break
                    break
        except Exception as e:
            print("run error!! : ", e)
        finally:
            cap.release()
            self.M_Info.stop()
            cv2.destroyAllWindows()
            print("touch free 종료..")
