import numpy as np
from pynput import mouse

import cv2
from PIL import ImageGrab

from datetime import datetime

import pygetwindow
class PaintBoard:
    def __init__(self,mode="static",window_name="PaintBoard"):
        self.img = None
        self.canvas= None
        self.drawing = False
        self.erasing = False
        self.status = '?'

        self.mode=mode
        self.window_name=window_name
        self.ix, self.iy = -1, -1

    def Savefile(self):
        ##차후에 윈도우 저장 메세지 박스?
        def masking(image, mask):
            # 이미지 크기 얻기
            height, width = image.shape[:2]
            # 마스크 적용
            masked_image = np.where(mask[:, :], mask, image)
            return masked_image
        
        current_time = datetime.now()
        filepath = current_time.strftime("%Y%m%d_%H%M%S")+'.png'
        cv2.imwrite(filepath,self.img)
        
    def on_click(self, event, x, y, flags, param):
        def drawLine(x,y):
                cv2.line(self.canvas, (self.ix, self.iy), (x, y), (0, 255, 0), 20)
        
        def erase(x,y,radius):
            cv2.circle(self.canvas,(x,y),radius,(0,0,0),-1)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                drawLine(x,y)
                self.ix, self.iy = x, y
            elif self.erasing:
                erase(x,y,25)
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.erasing = True
        elif event == cv2.EVENT_RBUTTONUP:
            self.erasing = False



    def showimg(self):
        def masking(image, mask):
            # 이미지 크기 얻기
            height, width = image.shape[:2]
            
            # 배경 이미지 생성
            # background = np.full((height, width, 3), background_color, dtype=np.uint8)

            # 마스크 적용
            masked_image = np.where(mask[:, :], mask, image)

            return masked_image
        
        masked_image=masking(self.img,self.canvas)
        cv2.imshow(self.window_name, masked_image)

    def run(self):
        def capture_screen():
            # 화면 캡처
            screenshot = ImageGrab.grab()
            # PIL 이미지를 numpy 배열로 변환
            screenshot_np = np.array(screenshot)
            # BGR에서 RGB로 변환
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
            return screenshot_rgb
        

        self.img = capture_screen()
        self.canvas =np.zeros_like(self.img)

        
        cv2.namedWindow(self.window_name,cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.window_name, self.on_click)
        
        cv2.imshow(self.window_name,self.img)
        w=pygetwindow.getWindowsWithTitle(self.window_name)
        w[0].activate()
        if(self.mode == 'static'):
            try:
                while True:
                    self.showimg()
                    if cv2.waitKey(1) & 0xFF == ord('q') or self.status=='quit_drawing':
                        self.Savefile()
                        break
            except Exception as e:
                print("run error!! : ", e)
            finally:
                cv2.destroyWindow(self.window_name)

if __name__ == "__main__":
    B=PaintBoard()
    B.run()
   
        
        



