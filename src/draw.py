import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import time
import threading
from queue import Queue

class StrokeBuilder:
    def __init__(self):
        self.stroke = []
        self.tmp = []

    def commit(self):
        if self.tmp:
            self.stroke.append(self.tmp)
            self.tmp = []

    def add(self, point):
        self.tmp.append(point)

    def build(self):
        return self.stroke

    def from_image(self, img, threshold1=120, threshold2=150):
        img_edge = self._preprocess(img, threshold1, threshold2)
        return self._generate_stroke(img_edge)

    def _preprocess(self, img, threshold1, threshold2):
        im_deno = cv2.GaussianBlur(img, (5, 5), 0)
        return 255 - cv2.Canny(im_deno, threshold1, threshold2)

    def _generate_stroke(self, img_bin):
        for x in range(img_bin.shape[0]):
            for y in range(img_bin.shape[1]):
                if img_bin[x][y] == 0:
                    self._process_pixel(x, y, img_bin)
                    self.commit()
        return self.stroke

    def _process_pixel(self, x, y, img_bin):
        stack = [(x, y)]
        while stack:
            px, py = stack.pop()
            if 0 <= px < img_bin.shape[0] and 0 <= py < img_bin.shape[1] and img_bin[px][py] == 0:
                img_bin[px][py] = 255
                self.add([py, px])
                stack.extend([(px+1, py), (px-1, py), (px, py+1), (px, py-1)])

def get_clipboard_image():
    img = ImageGrab.grabclipboard()
    if img:
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return None

class SafetyMonitor:
    def __init__(self):
        self._running = False
        self.emergency_stop = False
        self.event_queue = Queue()
        self._right_press_time = 0
        self.screen_width, self.screen_height = pyautogui.size()
        
    def start(self):
        self._running = True
        def monitor():
            while self._running and not self.emergency_stop:
                # 通过连续两次检测提高可靠性
                try:
                    # 优化后的安全检测
                    current_pos = pyautogui.position()
                    right_held = pyautogui.mouseDown(button='right')
                    in_corner = (
                        current_pos.x > self.screen_width - 15 and 
                        current_pos.y > self.screen_height - 15
                    )
                    
                    # 更新右键按压时间
                    if right_held and self._right_press_time == 0:
                        self._right_press_time = time.time()
                    elif not right_held:
                        self._right_press_time = 0
                    
                    # 触发条件：右键长按1.5秒或进入右下角区域
                    if (right_held and time.time() - self._right_press_time > 1.5) or in_corner:
                        if in_corner:
                            pyautogui.FAILSAFE = False  # 临时禁用内置安全机制
                        self.emergency_stop = True
                except Exception as e:
                    print(f"安全监控异常: {str(e)}")
                    self.emergency_stop = True
                    self.emergency_stop = True
                    self.event_queue.put(('emergency', time.time()))
                time.sleep(0.05)
        threading.Thread(target=monitor, daemon=True).start()
        
    def stop(self):
        self._running = False

def smooth_path(points, window_size=3):
    """使用滑动窗口平均算法平滑路径"""
    smoothed = []
    for i in range(len(points)):
        x = np.mean([p[0] for p in points[max(0,i-window_size):i+window_size]])
        y = np.mean([p[1] for p in points[max(0,i-window_size):i+window_size]])
        smoothed.append((x,y))
    return smoothed

def draw_stroke(stroke, start_point, config, safety_mon=None):
    pyautogui.PAUSE = config.get('move_delay', 0)
    emergency_triggered = False
    
    for i, path in enumerate(stroke):
        if safety_mon and safety_mon.emergency_stop:
            emergency_triggered = True
            break
            
        if len(path) > 1:
            # 路径平滑处理
            if config.get('path_smoothing', True):
                points = smooth_path(path)
            else:
                points = path
                
            points = np.array(points) * config['scale'] + start_point
            start = tuple(map(int, points[0]))
            
            try:
                pyautogui.moveTo(*start, duration=0.1)
                pyautogui.mouseDown()
                
                for point in points[1:]:
                    if safety_mon and safety_mon.emergency_stop:
                        raise KeyboardInterrupt
                    target = tuple(map(int, point))
                    pyautogui.moveTo(*target, duration=0.05)
                    
                pyautogui.mouseUp()
                
            except KeyboardInterrupt:
                emergency_triggered = True
                break
            
            # 添加笔画间隔
            time.sleep(config.get('stroke_delay', 0.1))
            
    if emergency_triggered:
        pyautogui.mouseUp()
        raise SystemExit("紧急终止：检测到鼠标右键按下")

def countdown(seconds=5):
    for i in range(seconds, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
