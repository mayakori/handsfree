import numpy as np
import tensorflow as tf
from math import dist
from tensorflow.lite.python.interpreter import Interpreter

model_path = './ttttt/test_model.tflite'

interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Input/Output Tensor 정보 얻기
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


JOINT_INDICES = np.array([[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19],
                          [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]])

seq = []
action_seq = []

actions = ['point', 'click']
seq_length = 30

EPSILON = 0.05
def gesture_recognition_lstm(joint_data):
    global cur_action
    #===========================================
    def temp(joint_data):#함수이름 일단 temp로해뒀습니다.
        global EPSILON
        thumb_1=joint_data[4]#엄지 끝좌표
        index_1=joint_data[8]#thumb_2,검지 끝좌표
        mid_1=joint_data[12]#thumb_3, 중지 끝좌표
        index_2=joint_data[6]#fing_2, 검지 root
        index_3=joint_data[7]#fing_2_1, 검지 중간

        
        if(dist(thumb_1,index_1)<=EPSILON):#검지 엄지 붙임
            return 'drag'
        if(dist(index_1,mid_1)<=EPSILON and dist(thumb_1,index_2)<=EPSILON):
            return 'right'
        
    cur_action = temp(joint_data)
    if cur_action=='drag' or cur_action == 'right':
        return cur_action
    ##===========================================
    
    v1 = joint_data[JOINT_INDICES[0], :3]  # Parent joint
    v2 = joint_data[JOINT_INDICES[1], :3]  # Child joint
    v = v2 - v1
    
    v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

    angle = np.arccos(np.einsum('nt,nt->n', v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:],
                                       v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:]))

    angle = np.degrees(angle)

    d = np.concatenate([joint_data.flatten(), angle])

    seq.append(d)
    # seq deque에 30개의 요소가 있을 때만 데이터를 추가하고, 그 외에는 추가하지 않습니다.
    if len(seq) < seq_length:
        return 'waiting_for_data'
    
    #input_data = np.expand_dims(np.array(seq, dtype=np.float32), axis=0)
    input_data = np.expand_dims(np.array(seq[-seq_length:], dtype=np.float32), axis=0)
    
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Get the output tensor from the interpreter
    output_data = interpreter.get_tensor(output_details[0]['index'])

    y_pred = output_data.squeeze()

    i_pred = int(np.argmax(y_pred))
    conf = y_pred[i_pred]

    #print("conf :", conf)
    
    if conf < 0.9:
        return 'waiting_for_data'

    action = actions[i_pred]
    action_seq.append(action)

    if len(action_seq) < 2:
        return 'waiting_for_data'

    cur_action = '?'
    if action_seq[-1] == action_seq[-2]:
        cur_action = action
    action_seq.pop(0)
    
    return cur_action
'''
---------------------------------------------------
학습한 LSTM이 추론한 제스처와 gesture recognizer가 추론한 제스처
비교 및 추론 값들을 사용해서 새로운 gesture event를 return 하는 함수
'''
#status 파라미터는 학습한 LSTM 모델이 추론한 제스처
#m_gesture 파라미터는 gesture recognizer가 추론한 제스처
is_clicked = False
def gesture_event(lstm_gesture,recognizer_gesture):
    global is_clicked
    gesture = '?'
    #print(lstm_gesture)
    #print(recognizer_gesture)
    #Closed_Fist
    if recognizer_gesture =='Thumb_Up':
        gesture = 'drawing'
    elif recognizer_gesture =='Thumb_Down':
        gesture = 'quit_drawing'
    elif lstm_gesture == 'drag':
        gesture = 'drag'
    elif lstm_gesture == 'right':
        gesture = 'right'
    elif (recognizer_gesture == 'Pointing_Up' or lstm_gesture == 'point'):
        gesture = 'point'
    elif is_clicked:#클릭 여러번 방지
        gesture = 'clicked'
    elif lstm_gesture == 'click':
        gesture = 'click'

    if gesture == 'click' or gesture =='clicked':
        is_clicked = True
    else:
        is_clicked = False
    
    return gesture
