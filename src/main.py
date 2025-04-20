# -*- coding: utf-8 -*-
import argparse
import time
import cv2
import pyautogui
import configparser
from draw import StrokeBuilder, draw_stroke, countdown, SafetyMonitor
from analysis import LineArtGenerator

def load_config():
    config = configparser.ConfigParser()
    config.read('src/config.ini')
    return {
        'threshold1': config.getint('EdgeDetection', 'threshold1'),
        'threshold2': config.getint('EdgeDetection', 'threshold2'),
        'scale': config.getfloat('Drawing', 'scale'),
        'move_delay': config.getfloat('Drawing', 'move_delay'),
        'stroke_delay': config.getfloat('Drawing', 'stroke_delay'),
        'enable_emergency': config.getboolean('Safety', 'enable_emergency')
    }

def main():
    # 加载配置并解析命令行参数
    config = load_config()
    parser = argparse.ArgumentParser(description="DrawGuess 自动绘画脚本")
    parser.add_argument("--threshold1", type=int, default=config['threshold1'],
                       help=f"Canny弱阈值 (默认: {config['threshold1']})")
    parser.add_argument("--threshold2", type=int, default=config['threshold2'],
                       help=f"Canny强阈值 (默认: {config['threshold2']})")
    parser.add_argument("--scale", type=float, default=config['scale'],
                       help=f"绘图缩放比例 (默认: {config['scale']})")
    parser.add_argument("--move-delay", type=float, default=config['move_delay'],
                       help=f"移动延迟时间(s) (默认: {config['move_delay']})")
    parser.add_argument("--stroke-delay", type=float, default=config['stroke_delay'],
                       help=f"笔画间隔时间(s) (默认: {config['stroke_delay']})")
    parser.add_argument("--preview", action="store_true",
                       help="预览线稿模式")
    parser.add_argument("--disable-emergency", action="store_false",
                       dest="enable_emergency", 
                       help="禁用右键紧急终止功能")
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

    # 初始化安全监控
    safety_mon = SafetyMonitor() if args.enable_emergency else None
    if safety_mon:
        safety_mon.start()

    # 开始绘制
    try:
        countdown(5)
        draw_config = {
            'scale': args.scale,
            'move_delay': args.move_delay,
            'stroke_delay': args.stroke_delay
        }
        draw_stroke(stroke, start_point, draw_config, safety_mon)
    except pyautogui.FailSafeException:
        print("\n安全停止: 鼠标移动到屏幕角落中断了绘制")

if __name__ == "__main__":
    main()
