# -*- coding: utf-8 -*-
import argparse
import time
import cv2
import pyautogui
from draw import StrokeBuilder, draw_stroke, countdown
from analysis import LineArtGenerator

def main():
    parser = argparse.ArgumentParser(description="DrawGuess 自动绘画脚本")
    parser.add_argument("--threshold1", type=int, default=120, 
                       help="Canny弱阈值 (默认: 120)")
    parser.add_argument("--threshold2", type=int, default=150,
                       help="Canny强阈值 (默认: 150)")
    parser.add_argument("--scale", type=float, default=1.0,
                       help="绘图缩放比例 (默认: 1.0)")
    parser.add_argument("--preview", action="store_true",
                       help="预览线稿模式")
    args = parser.parse_args()

    # 生成线稿并获取路径
    try:
        generator = LineArtGenerator()
        line_art_path = generator.process_clipboard(args.threshold1, args.threshold2)
        line_art_img = cv2.imread(line_art_path, cv2.IMREAD_GRAYSCALE)
    except Exception as e:
        print(f"错误: {str(e)}")
        return

    # 生成笔画数据
    builder = StrokeBuilder()
    stroke = builder.from_image(line_art_img, args.threshold1, args.threshold2)
    
    if args.preview:  # 预览模式
        cv2.imshow(u"Preview", line_art_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # 获取起始点
    print("\n请将鼠标移动到画布左上角...")
    time.sleep(8)
    start_point = pyautogui.position()
    print(f"设置画布原点: {start_point}")

    # 开始绘制
    try:
        countdown(5)
        draw_stroke(stroke, start_point, args.scale)
    except pyautogui.FailSafeException:
        print("\n安全停止: 鼠标移动到屏幕角落中断了绘制")

if __name__ == "__main__":
    main()
