# 绘图与数据分析项目

本项目用于实现数据分析和可视化绘图功能，生成 PNG 格式的结果图像。

## 主要功能

- 数据加载与预处理
- 统计分析与计算
- 可视化图表生成
- PNG 图像导出
- 批处理支持

## 环境要求

- Python 3.8+
- 依赖库：numpy, matplotlib, pandas

## 项目结构

```
try/
├── .git/            # 版本控制目录
├── data/            # 数据存储
│   ├── input/       # 原始数据
│   └── output/      # 生成图像
├── src/             # 源代码
│   ├── analysis.py  # 数据分析模块
│   ├── draw.py      # 绘图功能模块
│   └── main.py      # 主程序入口
├── .gitignore       # 版本控制排除配置
└── README.md        # 项目文档
```

## 快速开始

1. 克隆仓库

```bash
git clone https://github.com/aDarkMaker/YouDrawIGuess.git
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 运行主程序

用电脑自带的剪切板将图片剪切到剪切板中，然后运行以下命令：

```bash
python src/main.py
```

## 配置说明

`.gitignore`文件已配置排除：

- Python 编译文件(\*.pyc, **pycache**等)
- 虚拟环境相关文件
- IDE 配置文件(.vscode, .idea)
- 系统临时文件(.DS_Store 等)
- 图像文件(_.png, _.jpg)
