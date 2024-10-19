from pynput import mouse
from paintscreen import PaintBoard
import threading
###커서 처리용 코드

##해상도 저장용 클래스
class ResContainer:
    def __init__(self,LT,RB,CamRes_x,CamRes_y,monitor_width,monitor_height):
        self.LT_x, self.LT_y = LT[0], LT[1]
        self.RB_x, self.RB_y = RB[0], RB[1]
        self.CamRes_x,self.CamRes_y=CamRes_x,CamRes_y
        self.monitor_width,self.monitor_height = monitor_width,monitor_height
        
class MouseInfo:
    def __init__(self,poslen,controller):
        self.cntr=controller      ##컨트롤러 핸들값
        # self.listener = mouse.Listener(
        #     on_click=self.on_click)
        self.pressed=False
        self.prevpos=[]             ##poslen 갯수만큼 이전 위치를 저장함
        for i in range(0,poslen):
            self.prevpos.append(self.cntr.position)
        self.pb = PaintBoard()
        self.thread = None

        # self.listener.start()
    def on_click(self,x,y,btn,pressed):
        self.pressed=pressed
        print(self.pressed)
        
    ##위치 캐시 갱신용 메서드
    def PosAppend(self,input):
        del self.prevpos[0]      
        self.prevpos.append(input)

    ##위치 캐시의 평균값 반환
    def PrevPosAvg(self):
        sum_x=0
        sum_y=0
        for i in self.prevpos:
            sum_x+=i[0]
            sum_y+=i[1]
        l=len(self.prevpos)
        return (int(sum_x/l),int(sum_y/l))
    
    ##감지된 마우스 위치의 상대값을 반환함
    def Parse_Relative_Pos(self,pointer_pos,Res_Con):#########
        x_tip, y_tip = pointer_pos[:2]
        x_tip, y_tip = x_tip * 1280, y_tip * 720#캠 화면에서의 좌표
        #print(f'{x_tip}, {y_tip}')

        # 좌표를 LT와 RB 사이로 조정, 특정 영역 안에서만 mouse event
        x_tip = max(Res_Con.LT_x, min(Res_Con.RB_x, x_tip))
        y_tip = max(Res_Con.LT_y, min(Res_Con.RB_y, y_tip))
        # 사각형 영역 내에서의 상대 좌표를 구함
        relative_x = (x_tip - Res_Con.LT_x) / (Res_Con.RB_x - Res_Con.LT_x)
        relative_y = (y_tip - Res_Con.LT_y) / (Res_Con.RB_y - Res_Con.LT_y)
        #print(f'{relative_x}, {relative_y}')
        # 손의 위치를 모니터에 1:1 매칭시키기 위해 좌표를 조정
        move_x = max(0, min(relative_x * Res_Con.monitor_width, Res_Con.monitor_width))
        move_y = max(0, min(relative_y * Res_Con.monitor_height, Res_Con.monitor_height))
        #print(f'{move_x}, {move_y}')
        #mouse.position = (move_x, move_y)
        return (move_x,move_y)
    
    def interpolation(self):
        vec= []
        for i in range(1,len(self.prevpos)):
            vec.append(self.prevpos[i]-self.prevpos[i-1])
        
    def Refresh_Mouse_Pos(self,index_finger,Res_Con,gesture_event):
        new_pos=self.Parse_Relative_Pos(index_finger,Res_Con)   ##새로 읽어낸 마우스 위치
        threshold=12 #임계값 넘어야 마우스 위치 갱신함
        sum=0
        for i in zip(self.prevpos[-1:][0],new_pos):
            diff=i[1]-i[0]
            sum+=diff*diff
        #print(sum)
        if(sum>threshold**2):
            self.PosAppend(new_pos)
        
##        new_pos=self.Parse_Relative_Pos(index_finger,Res_Con)   ##새로 읽어낸 마우스 위치
##        self.PosAppend(new_pos)
            
        self.cntr.position=(self.prevpos[-1])                
        if(gesture_event=='point'):
           if(self.pressed==True):
               self.pressed=False
               self.cntr.release(mouse.Button.left)
        elif(gesture_event=='drag'):            
            # self.cntr.position = self.prevpos[-2]
            # self.cntr.press(mouse.Button.left)
            # self.cntr.position=self.prevpos[-1]
            # self.cntr.release(mouse.Button.left)
            
            if(self.pressed==False):
                self.pressed=True
                self.cntr.press(mouse.Button.left)
        elif(gesture_event=='click'):
            self.cntr.click(mouse.Button.left,1)
        elif(gesture_event=='right'):
            self.cntr.click(mouse.Button.right,1)
        elif(gesture_event=='drawing' and self.pb.status!='drawing'):
            self.pb.status=gesture_event
            self.thread = threading.Thread(target=self.pb.run)
            self.thread.daemon = True
            self.thread.start()
        elif(gesture_event=='erase' and self.pb.status=='drawing'):
            self.pb.status=gesture_event
        elif(gesture_event=='quit_drawing' and self.pb.status=='drawing'):
            self.pb.status=gesture_event
            if self.thread is not None:
                self.thread.join()
            
    def stop(self):
        #  self.listener.stop()
        if self.pb.status=='drawing':
            self.pb.status = 'quit_drawing'
            self.thread.join()
