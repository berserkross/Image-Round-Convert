from PIL import Image, ImageDraw, ImageTk
import os
import subprocess
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

# 定义支持的格式常量，便于维护
SUPPORTED_INPUT_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ico')
SUPPORTED_OUTPUT_FORMATS = ('png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp', 'ico')


def add_rounded_corners(image_path, output_path, radius):
    """
    给图片添加圆角效果

    参数:
        image_path (str): 输入图片的路径
        output_path (str): 输出图片的路径
        radius (int): 圆角的半径（像素）
    """
    try:
        # 清理路径字符串（去除可能的引号）
        image_path = image_path.strip().strip('"').strip("'")
        output_path = output_path.strip().strip('"').strip("'")

        # 检查输入文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"输入文件不存在: {image_path}")

        # 尝试打开图片，使用 with 语句确保资源释放
        with Image.open(image_path) as image:
            # 转换为RGBA模式（支持透明度）
            image = image.convert("RGBA")

            # 边界检查：半径不能为负数，且不应超过图片最小边长的一半
            if radius < 0:
                raise ValueError("半径不能为负数")
            max_radius = min(image.width, image.height) // 2
            if radius > max_radius:
                radius = max_radius

            # 创建一个与原图相同大小的透明遮罩层
            mask = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(mask)

            # 在遮罩层上绘制一个白色圆角矩形
            draw.rounded_rectangle((0, 0, image.width, image.height), radius, fill=(255, 255, 255, 255))

            # 将原图与遮罩合成，应用圆角效果
            result = Image.new("RGBA", image.size)
            result.paste(image, mask=mask)

            # 根据输出路径扩展名确定保存格式
            _, ext = os.path.splitext(output_path.lower())

            # 针对 ICO 格式的特殊处理
            if ext == '.ico':
                # ICO 格式通常要求较小的尺寸，Pillow 支持保存，但过大尺寸可能报错或不被某些系统识别
                # 这里保持原尺寸保存，但需确保模式兼容。Pillow 处理 ICO 时通常接受 RGBA
                try:
                    result.save(output_path, format='ICO')
                except Exception as e:
                    # 如果直接保存失败，可能是因为尺寸过大或颜色模式问题，尝试转换或提示
                    # 为了保持功能简单，这里记录错误并返回
                    return False, f"保存 ICO 格式失败: {e}"
            elif ext == '.jpg' or ext == '.jpeg':
                # JPG不支持透明度，转换为RGB
                result = result.convert("RGB")
                result.save(output_path, "JPEG")
            elif ext in ['.png', '.bmp', '.tiff', '.webp']:
                # 保存为相应格式
                result.save(output_path)
            else:
                # 默认保存为PNG格式
                result.save(output_path, "PNG")

        print(f"圆角图片已保存至: {output_path}")
        return True, f"圆角图片已保存至: {output_path}"

    except FileNotFoundError as e:
        return False, f"文件错误: {e}"
    except ValueError as e:
        return False, f"参数错误: {e}"
    except Exception as e:
        return False, f"处理图片时出错: {e}"


def open_image(file_path):
    """
    在不同操作系统上打开图片文件

    参数:
        file_path (str): 图片文件的路径
    """
    try:
        system = platform.system()
        if system == 'Windows':
            os.startfile(file_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        print(f"正在打开图片: {file_path}")
    except Exception as e:
        print(f"无法自动打开图片: {e}")


class BatchProcessGUI:
    def __init__(self, parent):
        self.parent = parent
        self.batch_window = tk.Toplevel(parent.root)
        self.batch_window.title("批量处理图片")
        self.batch_window.geometry("750x750")
        self.batch_window.resizable(True, True)

        # 设置变量
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.path.expanduser("~\\Desktop"))  # 默认为桌面
        self.radius = tk.StringVar(value="50")
        self.output_format = tk.StringVar(value="png")
        self.naming_rule = tk.StringVar(value="原文件名_圆角")
        self.file_counter = 1

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.batch_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(main_frame, text="批量处理图片", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 输入文件夹
        input_folder_frame = tk.Frame(main_frame)
        input_folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_folder_frame, text="输入文件夹:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(input_folder_frame, textvariable=self.input_folder, state="readonly", width=45).pack(side=tk.LEFT,
                                                                                                      padx=(10, 5),
                                                                                                      fill=tk.X,
                                                                                                      expand=True)
        tk.Button(input_folder_frame, text="选择", command=self.select_input_folder).pack(side=tk.LEFT)

        # 输出文件夹
        output_folder_frame = tk.Frame(main_frame)
        output_folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_folder_frame, text="输出文件夹:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(output_folder_frame, textvariable=self.output_folder, state="readonly", width=45).pack(side=tk.LEFT,
                                                                                                        padx=(10, 5),
                                                                                                        fill=tk.X,
                                                                                                        expand=True)
        tk.Button(output_folder_frame, text="选择", command=self.select_output_folder).pack(side=tk.LEFT)

        # 圆角半径
        radius_frame = tk.Frame(main_frame)
        radius_frame.pack(fill=tk.X, pady=5)
        tk.Label(radius_frame, text="圆角半径:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(radius_frame, textvariable=self.radius, width=10).pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(radius_frame, text="像素 (推荐: 50)").pack(side=tk.LEFT)

        # 输出格式
        format_frame = tk.Frame(main_frame)
        format_frame.pack(fill=tk.X, pady=5)
        tk.Label(format_frame, text="输出格式:", width=12, anchor="w").pack(side=tk.LEFT)

        # 使用Combobox替代Entry，提供可选格式
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format, width=10, state="readonly")
        format_combo['values'] = SUPPORTED_OUTPUT_FORMATS
        format_combo.pack(side=tk.LEFT, padx=(10, 5))

        tk.Label(format_frame, text="(选择输出图片格式)").pack(side=tk.LEFT)

        # 命名规则 - 改进的用户界面
        naming_frame = tk.Frame(main_frame)
        naming_frame.pack(fill=tk.X, pady=10)

        # 命名规则标题和说明
        naming_title_frame = tk.Frame(naming_frame)
        naming_title_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(naming_title_frame, text="输出文件名规则:", font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(naming_title_frame, text="(点击下方按钮快速设置命名规则)", font=("微软雅黑", 9), fg="gray").pack(
            side=tk.LEFT, padx=(10, 0))

        # 命名规则预览
        preview_frame = tk.Frame(naming_frame, relief=tk.GROOVE, bd=1, padx=10, pady=5)
        preview_frame.pack(fill=tk.X, pady=5)
        tk.Label(preview_frame, text="预览:", font=("微软雅黑", 9)).pack(side=tk.LEFT)
        self.preview_label = tk.Label(preview_frame, text="example_圆角.png", font=("微软雅黑", 9), fg="blue")
        self.preview_label.pack(side=tk.LEFT, padx=(10, 0))

        # 命名规则按钮组
        button_frame = tk.Frame(naming_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # 第一行按钮
        row1_frame = tk.Frame(button_frame)
        row1_frame.pack(fill=tk.X, pady=2)
        tk.Button(row1_frame, text="原文件名_圆角", command=lambda: self.set_naming_rule("原文件名_圆角"),
                  width=15, bg="#E3F2FD").pack(side=tk.LEFT, padx=2)
        tk.Button(row1_frame, text="原文件名_rounded", command=lambda: self.set_naming_rule("原文件名_rounded"),
                  width=15, bg="#E3F2FD").pack(side=tk.LEFT, padx=2)
        tk.Button(row1_frame, text="圆角_序号", command=lambda: self.set_naming_rule("圆角_序号"),
                  width=15, bg="#E3F2FD").pack(side=tk.LEFT, padx=2)

        # 第二行按钮
        row2_frame = tk.Frame(button_frame)
        row2_frame.pack(fill=tk.X, pady=2)
        tk.Button(row2_frame, text="自定义命名...", command=self.custom_naming_dialog,
                  width=15, bg="#FFF3E0").pack(side=tk.LEFT, padx=2)
        tk.Button(row2_frame, text="添加日期", command=self.add_date_to_naming,
                  width=15, bg="#E8F5E8").pack(side=tk.LEFT, padx=2)
        tk.Button(row2_frame, text="清空重设", command=lambda: self.set_naming_rule(""),
                  width=15, bg="#FFEBEE").pack(side=tk.LEFT, padx=2)

        # 当前命名规则显示
        current_rule_frame = tk.Frame(naming_frame)
        current_rule_frame.pack(fill=tk.X, pady=5)
        tk.Label(current_rule_frame, text="当前规则:", font=("微软雅黑", 9)).pack(side=tk.LEFT)
        self.current_rule_entry = tk.Entry(current_rule_frame, textvariable=self.naming_rule,
                                           width=50, state="readonly", font=("微软雅黑", 9))
        self.current_rule_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # 文件列表
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Label(list_frame, text="待处理文件列表:", font=("微软雅黑", 10, "bold")).pack(anchor="w")

        # 创建Treeview显示文件列表
        columns = ('文件名', '大小', '类型')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.file_tree.heading('文件名', text='文件名')
        self.file_tree.heading('大小', text='大小')
        self.file_tree.heading('类型', text='类型')
        self.file_tree.column('文件名', width=300)
        self.file_tree.column('大小', width=100)
        self.file_tree.column('类型', width=80)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 操作按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="刷新文件列表", command=self.refresh_file_list,
                  bg="#FF9800", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="开始批量处理", command=self.start_batch_process,
                  bg="#4CAF50", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="关闭", command=self.batch_window.destroy,
                  bg="#f44336", fg="white", width=10).pack(side=tk.LEFT, padx=5)

        # 绑定事件
        self.naming_rule.trace('w', self.update_preview)
        self.output_format.trace('w', self.update_preview)

    def set_naming_rule(self, rule_template):
        """设置命名规则模板"""
        if rule_template == "原文件名_圆角":
            self.naming_rule.set("原文件名_圆角")
        elif rule_template == "原文件名_rounded":
            self.naming_rule.set("原文件名_rounded")
        elif rule_template == "圆角_序号":
            self.naming_rule.set("圆角图片_")
            self.file_counter = 1
        else:
            self.naming_rule.set("")

    def custom_naming_dialog(self):
        """自定义命名规则对话框"""
        dialog = tk.Toplevel(self.batch_window)
        dialog.title("自定义命名规则")
        dialog.geometry("500x300")
        dialog.transient(self.batch_window)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="自定义文件名规则", font=("微软雅黑", 12, "bold")).pack(pady=(0, 10))

        # 说明文本
        help_text = """可在文件名中使用以下特殊标记：
        {name} - 原文件名
        {ext} - 文件扩展名
        {index} - 序号（自动编号）
        {date} - 当前日期

        示例：
        "我的图片_{name}_{index}" → "我的图片_照片_001.png"
        "{date}_处理后的图片" → "20240201_处理后的图片.png"
        """

        help_label = tk.Label(main_frame, text=help_text, justify=tk.LEFT, font=("微软雅黑", 9))
        help_label.pack(pady=10, anchor="w")

        # 输入框
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        tk.Label(input_frame, text="命名规则:").pack(side=tk.LEFT)
        custom_entry = tk.Entry(input_frame, width=40)
        custom_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        custom_entry.insert(0, self.naming_rule.get())

        # 按钮
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)

        def apply_custom():
            self.naming_rule.set(custom_entry.get())
            dialog.destroy()

        tk.Button(btn_frame, text="应用", command=apply_custom, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT,
                                                                                                         padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def add_date_to_naming(self):
        """在当前命名规则中添加日期"""
        current = self.naming_rule.get()
        if "{date}" not in current:
            self.naming_rule.set(current + "_{date}")

    def update_preview(self, *args):
        """更新文件名预览"""
        try:
            rule = self.naming_rule.get()
            format_ext = self.output_format.get()

            # 替换占位符生成预览
            preview = rule
            preview = preview.replace("{name}", "示例图片")
            preview = preview.replace("{ext}", format_ext)
            preview = preview.replace("{index}", "001")
            preview = preview.replace("{date}", "20240201")

            # 确保有扩展名
            if not preview.endswith(f".{format_ext}"):
                preview += f".{format_ext}"

            self.preview_label.config(text=preview)
        except:
            self.preview_label.config(text="预览生成错误")

    def select_input_folder(self):
        """选择输入文件夹"""
        folder_path = filedialog.askdirectory(title="选择输入图片文件夹")
        if folder_path:
            self.input_folder.set(folder_path)
            self.refresh_file_list()

    def select_output_folder(self):
        """选择输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_folder.set(folder_path)

    def refresh_file_list(self):
        """刷新文件列表"""
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        input_folder = self.input_folder.get()
        if not input_folder:
            return

        try:
            files = []
            for file in os.listdir(input_folder):
                if file.lower().endswith(SUPPORTED_INPUT_FORMATS):
                    file_path = os.path.join(input_folder, file)
                    # 检查是否是文件而非目录
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        size_str = f"{size / 1024:.1f}KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f}MB"
                        file_ext = os.path.splitext(file)[1].upper()
                        files.append((file, size_str, file_ext))

            # 按文件名排序
            files.sort(key=lambda x: x[0])

            # 插入到Treeview中
            for file, size, ext in files:
                self.file_tree.insert('', tk.END, values=(file, size, ext))

        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件夹: {e}")

    def start_batch_process(self):
        """开始批量处理"""
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()
        radius_str = self.radius.get()
        output_format = self.output_format.get()
        naming_rule = self.naming_rule.get()

        # 验证输入
        if not input_folder:
            messagebox.showerror("错误", "请选择输入文件夹")
            return

        if not output_folder:
            messagebox.showerror("错误", "请选择输出文件夹")
            return

        if not naming_rule:
            messagebox.showerror("错误", "请设置输出文件名规则")
            return

        try:
            radius = int(radius_str)
            if radius < 0:
                raise ValueError("半径不能为负数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的圆角半径（正整数）")
            return

        # 获取文件列表
        files = []
        try:
            for file in os.listdir(input_folder):
                if file.lower().endswith(SUPPORTED_INPUT_FORMATS):
                    full_path = os.path.join(input_folder, file)
                    if os.path.isfile(full_path):
                        files.append(file)
        except Exception as e:
            messagebox.showerror("错误", f"读取输入文件夹失败: {e}")
            return

        if not files:
            messagebox.showwarning("警告", "输入文件夹中没有找到支持的图片文件")
            return

        # 开始批量处理
        processed_count = 0
        failed_count = 0
        failed_files = []

        progress_window = tk.Toplevel(self.batch_window)
        progress_window.title("批量处理进度")
        progress_window.geometry("400x150")
        progress_window.transient(self.batch_window)
        progress_window.grab_set()

        progress_label = tk.Label(progress_window, text="正在处理...", font=("微软雅黑", 10))
        progress_label.pack(pady=20)

        progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=300)
        progress_bar.pack(pady=10)
        progress_bar['maximum'] = len(files)

        status_label = tk.Label(progress_window, text="", font=("微软雅黑", 9))
        status_label.pack(pady=5)

        # 重置计数器
        self.file_counter = 1

        for i, file in enumerate(files):
            try:
                input_path = os.path.join(input_folder, file)

                # 根据命名规则生成输出文件名
                file_name, original_ext = os.path.splitext(file)
                output_ext = output_format.lstrip('.')

                # 替换命名规则中的占位符
                from datetime import datetime
                output_name = naming_rule
                output_name = output_name.replace('{name}', file_name)
                output_name = output_name.replace('{ext}', output_ext)
                output_name = output_name.replace('{index}', f"{self.file_counter:03d}")
                output_name = output_name.replace('{date}', datetime.now().strftime("%Y%m%d"))

                # 移除非法文件名字符，并清理首尾空格和点号
                output_name = re.sub(r'[<>:"/\\|?*]', '', output_name)
                output_name = output_name.strip('. ')

                # 如果清理后文件名为空，使用默认名
                if not output_name:
                    output_name = "unnamed"

                # 确保输出文件名包含扩展名
                if not output_name.lower().endswith(f'.{output_ext}'):
                    output_name = f"{output_name}.{output_ext}"

                output_path = os.path.join(output_folder, output_name)

                # 处理图片
                success, message = add_rounded_corners(input_path, output_path, radius)

                if success:
                    processed_count += 1
                    self.file_counter += 1
                else:
                    failed_count += 1
                    failed_files.append(f"{file}: {message}")

            except Exception as e:
                failed_count += 1
                failed_files.append(f"{file}: {str(e)}")

            # 更新进度
            progress_bar['value'] = i + 1
            progress_label.config(text=f"正在处理: {file}")
            status_label.config(text=f"进度: {i + 1}/{len(files)} (成功: {processed_count}, 失败: {failed_count})")
            progress_window.update()

        # 处理完成
        progress_window.destroy()

        result_msg = f"批量处理完成!\n总文件数: {len(files)}\n成功处理: {processed_count}\n处理失败: {failed_count}"
        if failed_files:
            result_msg += "\n\n失败文件:\n" + "\n".join(failed_files[:5])  # 只显示前5个失败的文件
            if len(failed_files) > 5:
                result_msg += f"\n... 还有 {len(failed_files) - 5} 个文件失败"

        messagebox.showinfo("批量处理结果", result_msg)


class InstructionManual:
    def __init__(self, parent):
        self.parent = parent
        self.manual_window = tk.Toplevel(parent.root)
        self.manual_window.title("使用说明 - 图片转圆角工具")
        self.manual_window.geometry("800x600")
        self.manual_window.resizable(True, True)

        self.create_manual()

    def create_manual(self):
        # 主框架
        main_frame = tk.Frame(self.manual_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(main_frame, text="图片转圆角工具 - 使用说明书",
                               font=("微软雅黑", 16, "bold"), fg="#2E7D32")
        title_label.pack(pady=(0, 20))

        # 创建带滚动条的文本区域
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("微软雅黑", 10),
                              padx=10, pady=10, spacing1=5, spacing2=2, spacing3=5)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 插入使用说明内容
        manual_content = """
图片转圆角工具 - 使用说明书

一、工具简介
本工具是一款专业的图片处理软件，主要功能包括：
• 为图片添加圆角效果
• 支持多种图片格式转换
• 单张图片处理和批量处理模式
• 实时预览和自动打开结果

二、单张图片处理
1. 选择输入图片：点击"选择"按钮，选择要处理的图片
2. 设置输出文件夹：选择处理后的图片保存位置
3. 设置输出文件名：自定义输出图片的名称
4. 选择输出格式：支持PNG、JPG、BMP、TIFF、WebP、ICO等格式
5. 设置圆角半径：推荐值50像素，可根据需要调整
6. 点击"应用圆角"开始处理

三、批量处理功能
1. 点击主界面"批量处理"按钮进入批量模式
2. 选择输入文件夹：包含所有要处理的图片
3. 选择输出文件夹：处理后的图片保存位置
4. 设置输出格式：所有图片将统一转换为该格式
5. 设置圆角半径：统一应用于所有图片

四、文件名规则设置（新功能）
批量处理时，可以灵活设置输出文件名：

预设规则：
• 原文件名_圆角：保留原文件名，添加"_圆角"后缀
• 原文件名_rounded：英文命名风格
• 圆角_序号：按顺序编号，如"圆角图片_001.png"

高级功能：
• 自定义命名：使用{name}、{ext}、{index}、{date}等占位符
• 添加日期：自动在文件名中加入处理日期
• 实时预览：立即查看命名效果

占位符说明：
{name} - 原始文件名
{ext} - 文件扩展名
{index} - 自动序号（3位数字）
{date} - 处理日期（YYYYMMDD格式）

五、支持格式
输入格式：JPG、JPEG、PNG、BMP、GIF、TIFF、WebP、ICO
输出格式：PNG、JPG、JPEG、BMP、TIFF、WebP、ICO

六、注意事项
1. 圆角效果在透明背景的PNG格式下效果最佳
2. JPG格式不支持透明度，圆角区域将显示为白色
3. ICO格式通常用于图标，建议尺寸不宜过大
4. 建议先试用单张处理，确认效果后再进行批量处理
5. 批量处理前请备份原始图片

七、常见问题
Q: 为什么圆角效果不明显？
A: 可能是圆角半径设置过小，尝试增大半径值

Q: 处理后的图片大小变化很大？
A: 不同格式的压缩率不同，PNG为无损格式，JPG为有损压缩

Q: 批量处理时文件名混乱？
A: 检查命名规则，建议使用{index}占位符确保唯一性

技术支持：如有问题请联系开发者
版本：v2.0 (优化版)
        """

        text_widget.insert(tk.END, manual_content)
        text_widget.config(state=tk.DISABLED)  # 设置为只读

        # 关闭按钮
        close_btn = tk.Button(main_frame, text="关闭说明", command=self.manual_window.destroy,
                              bg="#f44336", fg="white", font=("微软雅黑", 10), width=15)
        close_btn.pack(pady=20)


class RoundedCornersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片转圆角工具 v2.0")
        self.root.geometry("650x450")
        self.root.resizable(True, True)

        # 设置变量
        self.input_path = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.path.expanduser("~\\Desktop"))  # 默认为桌面
        self.radius = tk.StringVar(value="50")
        self.output_format = tk.StringVar(value="png")

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(main_frame, text="图片转圆角工具 v2.0",
                               font=("微软雅黑", 16, "bold"), fg="#1565C0")
        title_label.pack(pady=(0, 20))

        # 版本说明
        version_label = tk.Label(main_frame, text="新增：智能批量命名规则 + 使用说明",
                                 font=("微软雅黑", 10), fg="#E65100")
        version_label.pack(pady=(0, 10))

        # 输入图片路径
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_frame, text="输入图片:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(input_frame, textvariable=self.input_path, state="readonly", width=40).pack(side=tk.LEFT, padx=(10, 5),
                                                                                             fill=tk.X, expand=True)
        tk.Button(input_frame, text="选择", command=self.select_input_image).pack(side=tk.LEFT)

        # 输出文件夹
        output_folder_frame = tk.Frame(main_frame)
        output_folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_folder_frame, text="输出文件夹:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(output_folder_frame, textvariable=self.output_folder, state="readonly", width=40).pack(side=tk.LEFT,
                                                                                                        padx=(10, 5),
                                                                                                        fill=tk.X,
                                                                                                        expand=True)
        tk.Button(output_folder_frame, text="选择", command=self.select_output_folder).pack(side=tk.LEFT)

        # 输出文件名
        output_name_frame = tk.Frame(main_frame)
        output_name_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_name_frame, text="输出文件名:", width=12, anchor="w").pack(side=tk.LEFT)
        self.output_name = tk.Entry(output_name_frame, width=40)
        self.output_name.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        tk.Label(output_name_frame, text=".").pack(side=tk.LEFT)

        # 使用Combobox替代Entry
        format_combo = ttk.Combobox(output_name_frame, textvariable=self.output_format, width=8, state="readonly")
        format_combo['values'] = SUPPORTED_OUTPUT_FORMATS
        format_combo.pack(side=tk.LEFT)

        # 圆角半径
        radius_frame = tk.Frame(main_frame)
        radius_frame.pack(fill=tk.X, pady=5)
        tk.Label(radius_frame, text="圆角半径:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(radius_frame, textvariable=self.radius, width=10).pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(radius_frame, text="像素 (推荐: 50)").pack(side=tk.LEFT)

        # 操作按钮 - 增加使用说明按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="应用圆角", command=self.apply_rounded_corners,
                  bg="#4CAF50", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="批量处理", command=self.open_batch_process,
                  bg="#2196F3", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="预览结果", command=self.preview_result,
                  bg="#FF9800", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="使用说明", command=self.show_instructions,
                  bg="#9C27B0", fg="white", width=12).pack(side=tk.LEFT, padx=5)  # 新增按钮
        tk.Button(button_frame, text="清空", command=self.clear_fields,
                  bg="#f44336", fg="white", width=12).pack(side=tk.LEFT, padx=5)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪 - 请选择输入图片和输出文件夹")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

    def select_input_image(self):
        """选择输入图片"""
        file_path = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp *.ico"),
                ("JPG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("BMP文件", "*.bmp"),
                ("GIF文件", "*.gif"),
                ("TIFF文件", "*.tiff"),
                ("WebP文件", "*.webp"),
                ("ICO文件", "*.ico"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.input_path.set(file_path)
            # 自动填充输出文件名
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_name.delete(0, tk.END)
            self.output_name.insert(0, f"{file_name}_rounded")
            self.status_var.set(f"已选择输入图片: {os.path.basename(file_path)}")

    def select_output_folder(self):
        """选择输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_folder.set(folder_path)
            self.status_var.set(f"已选择输出文件夹: {folder_path}")

    def apply_rounded_corners(self):
        """应用圆角效果"""
        input_path = self.input_path.get()
        output_folder = self.output_folder.get()
        output_name = self.output_name.get()
        output_format = self.output_format.get()
        radius_str = self.radius.get()

        # 验证输入
        if not input_path:
            messagebox.showerror("错误", "请选择输入图片")
            return

        if not output_folder:
            messagebox.showerror("错误", "请选择输出文件夹")
            return

        if not output_name:
            messagebox.showerror("错误", "请输入输出文件名")
            return

        if not output_format:
            messagebox.showerror("错误", "请输入输出格式")
            return

        try:
            radius = int(radius_str)
            if radius < 0:
                raise ValueError("半径不能为负数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的圆角半径（正整数）")
            return

        # 构建输出路径
        output_path = os.path.join(output_folder, f"{output_name}.{output_format.lstrip('.')}")

        # 应用圆角效果
        success, message = add_rounded_corners(input_path, output_path, radius)

        if success:
            self.status_var.set(message)
            # 询问是否打开图片
            if messagebox.askyesno("操作完成", "圆角处理成功！是否立即打开图片？"):
                open_image(output_path)
        else:
            self.status_var.set("处理失败")
            messagebox.showerror("处理失败", message)

    def open_batch_process(self):
        """打开批量处理界面"""
        batch_gui = BatchProcessGUI(self)

    def show_instructions(self):
        """显示使用说明"""
        InstructionManual(self)

    def preview_result(self):
        """预览结果（在新窗口中显示）"""
        input_path = self.input_path.get()
        if not input_path:
            messagebox.showerror("错误", "请先选择输入图片")
            return

        try:
            # 打开原图
            original_img = Image.open(input_path)
            original_img.show()
            self.status_var.set("正在显示原图预览")
        except Exception as e:
            messagebox.showerror("错误", f"无法预览原图: {e}")

    def clear_fields(self):
        """清空所有字段"""
        self.input_path.set("")
        self.output_folder.set(os.path.expanduser("~\\Desktop"))
        self.output_name.delete(0, tk.END)
        self.output_format.set("png")
        self.radius.set("50")
        self.status_var.set("就绪 - 请选择输入图片和输出文件夹")


def main():
    root = tk.Tk()
    app = RoundedCornersGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
