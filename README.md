# Batch Image Corner Rounding Tool (Supports Format Conversion)

批量图片圆角 + 格式转换桌面工具，基于 Python/Tkinter/Pillow。
支持单张处理与批量处理，可自定义圆角半径、输出格式、命名规则。

## Features
- 单张图片圆角：选择图片 → 设置半径/格式/文件名 → 导出
- 批量处理：选择输入文件夹，按命名模板批量输出
- 圆角半径边界保护：自动限制在 0~min(w,h)/2
- 支持输入：jpg/jpeg/png/bmp/gif/tiff/webp/ico
- 支持输出：png/jpg/jpeg/bmp/tiff/webp/ico
- JPG 自动转 RGB（去透明）；PNG 保留 RGBA 圆角透明
- 批量命名模板：原文件名_圆角、原文件名_rounded、圆角_序号、自定义
  - 占位符：{name} 原文件名、{ext} 扩展名、{index} 序号、{date} 日期
- 进度条 + 成功/失败统计；内置使用说明窗口

## Requirements
- Python 3.8+（建议；未在其他版本全面测试）
- Pillow
- Tkinter（CPython 标准库自带；Linux 可能需补 python3-tk）

## Install
git clone https://github.com/berserkross/Batch-Image-Corner-Rounding-Tool-Supports-Format-Conversion-.git
cd Batch-Image-Corner-Rounding-Tool-Supports-Format-Conversion-
pip install -r requirements.txt
# 若没有 requirements.txt：pip install Pillow

## Usage
python "Batch Image Corner Rounding Tool (Supports Format Conversion).py"

1. 单张：点击“选择”输入图片 → 设输出文件夹/文件名/格式/半径 → “应用圆角”
2. 批量：主界面“批量处理” → 选输入/输出文件夹 → 设半径、格式、命名规则 → “开始批量处理”
3. 命名预览：修改命名规则后界面实时预览，例如
   - 原文件名_圆角 + png → example_圆角.png
   - {date}_处理后的图片 + png → 20260908_处理后的图片.png

## Notes
- 圆角在透明背景 PNG 下效果最佳；JPG 圆角外区域会填白。
- ICO 建议小尺寸；大图存 ICO 可能被系统预览工具拒绝。
- 批量处理前建议备份原图。

## Project status
个人学习项目。当前为单文件实现，后续可拆为 CLI/库、增加圆角预览、增加阴影/描边。
