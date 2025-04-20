import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import time

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

def draw_stroke(stroke, start_point, resize=1):
    pyautogui.PAUSE = 0
    for path in stroke:
        if len(path) > 1:
            points = np.array(path) * resize + start_point
            pyautogui.moveTo(*points[0])
            pyautogui.mouseDown()
            for point in points[1:]:
                pyautogui.moveTo(*point)
            pyautogui.mouseUp()

def countdown(seconds=5):
    for i in range(seconds, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
