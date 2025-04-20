import cv2
import numpy as np
from PIL import ImageGrab, Image
import os


class LineArtGenerator:
    def __init__(self, output_dir="data"):
        """
        Args:
            output_dir: 输出目录路径 (默认data)
        """
        self.output_dir = output_dir
        self.counter = 1
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def _create_line_art(img, threshold1=80, threshold2=120):
        """
        Args:
            img: 输入图像(numpy数组)
            threshold1: Canny弱阈值 (默认180)
            threshold2: Canny强阈值 (默认250)
        Returns:
            线稿图像(numpy数组)
        """
        # 高斯去噪 + Canny边缘检测
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        edges = cv2.Canny(blurred, threshold1, threshold2)
        return 255 - edges  # 反色处理

    def process_clipboard(self, threshold1=80, threshold2=120):
        """处理剪切板图片"""
        clipboard_content = ImageGrab.grabclipboard()
        
        if clipboard_content is None:
            raise ValueError("剪切板内容为空")
            
        # 处理不同类型的剪切板内容
        if isinstance(clipboard_content, list):  # 文件路径列表
            img_path = clipboard_content[0]
            if not os.path.isfile(img_path):
                raise ValueError(f"无效的图片路径: {img_path}")
            img = Image.open(img_path)
        elif isinstance(clipboard_content, Image.Image):  # PIL图像对象
            img = clipboard_content
        else:  # 其他类型
            raise ValueError("不支持的剪切板内容类型")
            
        # 转换OpenCV格式（处理RGBA格式）
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # 生成线稿
        line_art = self._create_line_art(cv_img, threshold1, threshold2)
        
        # 保存结果
        output_path = os.path.join(self.output_dir, f"output{self.counter}.png")
        cv2.imwrite(output_path, line_art)
        self.counter += 1
        return output_path

    @classmethod
    def batch_process(cls, input_dir, output_dir, threshold1=80, threshold2=120): # 一般用不上
        """批量处理图片文件
        Args:
            input_dir: 输入图片目录
            output_dir: 输出目录
            threshold1: Canny弱阈值 (默认180)
            threshold2: Canny强阈值 (默认250)
        """
        os.makedirs(output_dir, exist_ok=True)
        processed = 0
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    img_path = os.path.join(input_dir, filename)
                    img = cv2.imread(img_path)
                    if img is None:
                        raise ValueError(f"无法读取图片文件: {img_path}")
                        
                    line_art = cls._create_line_art(img, threshold1, threshold2)
                    output_path = os.path.join(output_dir, f"line_{filename}")
                    cv2.imwrite(output_path, line_art)
                    processed += 1
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {str(e)}")

if __name__ == "__main__":
    generator = LineArtGenerator()
    try:
        saved_path = generator.process_clipboard()
        print(f"线稿已保存至：{saved_path}")
    except ValueError as e:
        print(str(e))
