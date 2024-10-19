from test_client_class import HandGesture
import ctypes

if __name__ == "__main__":
    """
    HandGesture 전달인자
    LT,RB,CamRes_x,CamRes_y,monitor_width=1920,monitor_height=1080
    LT,RB      카메라 내의 인식범위
    CamRes_x,CamRes_y   카메라 해상도
    monitor_width=1920,monitor_height=1080  모니터 해상도 기본값 1920*1080
    """
    
##    LT = (600, 450)
##    RB = (900, 650)
    LT = (int(1280/5*1.8),int( 720/5*1.8))
    RB = (int(1280/5*3.2), int(720/5*3.2))
    

    CamRes_x,CamRes_y=1280,720

    user32 = ctypes.windll.user32
    monitor_width = user32.GetSystemMetrics(0)
    monitor_height = user32.GetSystemMetrics(1)
    
    Touch_Free = HandGesture(LT,RB,CamRes_x,CamRes_y,monitor_width,monitor_height)
    Touch_Free.main()
