# src/gui/app.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import traceback
import os
from src.core.processor import HTSProcessor
from src.data.hts_data_loader import HTSDataLoader
from src.data.email_template_loader import EmailTemplateLoader
from src.utils.helpers import resource_path
from config.settings import HTS_DB_FILENAME, EMAIL_TEMPLATE_FILENAME


class HTSEmailGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTS 邮件生成器")
        self.root.geometry("800x600")

        # --- 文件路径 ---
        self.hts_db_path = resource_path(HTS_DB_FILENAME)
        self.blurb_file_path = resource_path(EMAIL_TEMPLATE_FILENAME)

        # --- 用于线程间通信的队列 ---
        self.log_queue = queue.Queue()

        # --- 核心处理器 ---
        self.processor: HTSProcessor = None

        # --- 创建 GUI 元素 ---
        self.create_widgets()

        # --- 检查并加载文件 ---
        self.check_and_load_files()

    def create_widgets(self):
        # --- 输入区域 ---
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="HTS 编码:").pack(side='left')
        self.entry_code = tk.Entry(input_frame, width=50)
        self.entry_code.pack(side='left', padx=(5, 0), fill='x', expand=True)
        self.entry_code.bind('<Return>', self.on_generate_click)

        self.btn_generate = tk.Button(input_frame, text="生成邮件", command=self.on_generate_click)
        self.btn_generate.pack(side='right', padx=(5, 0))

        # --- 输出区域 ---
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.text_output = scrolledtext.ScrolledText(output_frame, state='disabled', wrap='word')
        self.text_output.pack(fill='both', expand=True)

        # --- 状态栏 ---
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side='bottom', fill='x')

        # --- 配置文本框标签样式 ---
        self.text_output.tag_config("success", foreground="green")
        self.text_output.tag_config("error", foreground="red")

    def log_message(self, message):
        """向 GUI 文本框添加日志信息"""
        self.text_output.config(state='normal')
        if message.startswith("✅"):
            self.text_output.insert(tk.END, message, "success")
        elif message.startswith("❌"):
            self.text_output.insert(tk.END, message, "error")
        else:
            self.text_output.insert(tk.END, message)
        self.text_output.config(state='disabled')
        self.text_output.see(tk.END)

    def check_and_load_files(self):
        """检查文件是否存在并加载数据"""
        self.status_var.set("正在加载文件...")
        self.root.update()

        try:
            df_hts = HTSDataLoader.load_hts_database(self.hts_db_path)
            self.log_message(f"✅ HTS 数据库加载成功: {self.hts_db_path}\n")
        except Exception as e:
            error_msg = f"❌ 加载 HTS 数据库失败: {e}\n请确保 '{HTS_DB_FILENAME}' 文件存在于程序同目录下。\n"
            self.log_message(error_msg)
            self.status_var.set("加载 HTS 数据库失败")
            messagebox.showerror("错误", error_msg)
            return

        try:
            email_blurbs = EmailTemplateLoader.load_email_templates(self.blurb_file_path)
            self.log_message("✅ 邮件模板加载成功\n")
        except Exception as e:
            error_msg = f"❌ 加载邮件模板失败: {e}\n请确保 '{EMAIL_TEMPLATE_FILENAME}' 文件存在于程序同目录下。\n"
            self.log_message(error_msg)
            self.status_var.set("加载邮件模板失败")
            messagebox.showerror("错误", error_msg)
            return

        # 初始化核心处理器
        self.processor = HTSProcessor(df_hts, email_blurbs)

        self.status_var.set("文件加载完成，就绪")
        self.log_message("✅ 所有文件加载完成，可以开始生成邮件。\n")

    def on_generate_click(self, event=None):
        """当点击“生成邮件”按钮或按回车时触发"""
        if not self.processor:
            self.log_message("❌ 请先确保 HTS 数据库和邮件模板已成功加载。\n")
            return

        input_str = self.entry_code.get().strip()
        if not input_str:
            messagebox.showwarning("警告", "请输入至少一个 HTS 编码。")
            return

        codes = [code.strip() for code in input_str.split() if code.strip()]
        if not codes:
            messagebox.showwarning("警告", "请输入有效的 HTS 编码。")
            return

        self.btn_generate.config(state='disabled')
        self.entry_code.config(state='disabled')
        self.status_var.set("处理中...")

        threading.Thread(target=self.run_generation, args=(codes,), daemon=True).start()
        self.root.after(100, self.check_log_queue)

    def run_generation(self, codes):
        """在后台线程中执行邮件生成逻辑"""
        try:
            def gui_logger(msg):
                self.log_queue.put(msg)

            unique_codes = list(set(codes))
            for code in unique_codes:
                # 调用核心处理器
                self.processor.process_single_code(code, gui_logger)
            self.log_queue.put("所有编码处理完成。\n")
        except Exception as e:
            self.log_queue.put(f"❌ 处理过程中发生未预期错误: {e}\n")
            self.log_queue.put(f"Traceback: {traceback.format_exc()}\n")
        finally:
            self.log_queue.put("<<PROCESSING_COMPLETE>>")

    def check_log_queue(self):
        """在主线程中检查日志队列并更新 GUI"""
        try:
            while True:
                line = self.log_queue.get_nowait()
                if line == "<<PROCESSING_COMPLETE>>":
                    self.btn_generate.config(state='normal')
                    self.entry_code.config(state='normal')
                    self.status_var.set("处理完成")
                    break
                else:
                    self.log_message(line)
        except queue.Empty:
            self.root.after(100, self.check_log_queue)