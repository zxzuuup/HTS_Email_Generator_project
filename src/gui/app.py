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
        self.root.geometry("1000x700")  # 增大窗口尺寸

        # 历史记录存储
        self.history = []

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
        # 主容器使用网格布局
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # --- 输入区域 ---
        input_frame = tk.Frame(main_frame)
        input_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        tk.Label(input_frame, text="HTS 编码:").pack(side='left')
        self.entry_code = tk.Entry(input_frame, width=50)
        self.entry_code.pack(side='left', padx=(5, 0), fill='x', expand=True)
        self.entry_code.bind('<Return>', self.on_generate_click)

        self.btn_generate = tk.Button(input_frame, text="生成邮件", command=self.on_generate_click)
        self.btn_generate.pack(side='right', padx=(5, 0))

        # 复制按钮
        self.btn_copy = tk.Button(input_frame, text="复制内容", command=self.copy_content, state='disabled')
        self.btn_copy.pack(side='right', padx=(5, 0))

        # --- 历史记录区域 ---
        history_frame = tk.Frame(main_frame)
        history_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 10))
        tk.Label(history_frame, text="历史记录").pack(anchor='w')

        self.history_listbox = tk.Listbox(history_frame)
        self.history_listbox.pack(fill='both', expand=True, pady=(5, 0))
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        # --- 内容显示区域 ---
        content_frame = tk.Frame(main_frame)
        content_frame.grid(row=1, column=1, sticky='nsew')
        tk.Label(content_frame, text="邮件内容").pack(anchor='w')

        self.content_text = scrolledtext.ScrolledText(content_frame, wrap='word')
        self.content_text.pack(fill='both', expand=True, pady=(5, 0))

        # --- 日志区域 ---
        log_frame = tk.Frame(main_frame)
        log_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(10, 0))
        tk.Label(log_frame, text="日志信息").pack(anchor='w')

        self.text_output = scrolledtext.ScrolledText(log_frame, state='disabled', wrap='word', height=10)
        self.text_output.pack(fill='both', expand=True, pady=(5, 0))

        # --- 状态栏 ---
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side='bottom', fill='x')

        # 配置权重，使区域可伸缩
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)

        # 配置文本框标签样式
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
            # 获取处理结果
            results = self.processor.process_multi_code(unique_codes, gui_logger)
            self.log_queue.put("所有编码处理完成。\n")
            # 将结果放入队列处理
            self.log_queue.put(("RESULTS", results))
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
                # 处理结果数据
                elif isinstance(line, tuple) and line[0] == "RESULTS":
                    self.handle_results(line[1])
                else:
                    self.log_message(line)
        except queue.Empty:
            self.root.after(100, self.check_log_queue)

    def handle_results(self, results):
        """处理生成的邮件内容，更新历史记录"""
        for result in results:
            self.history.append(result)
            self.history_listbox.insert(tk.END, f"编码: {result['code']}")

        # 显示最后一个结果
        if results:
            self.display_content(results[-1])

    def display_content(self, result):
        """在界面上显示邮件内容"""
        self.content_text.delete(1.0, tk.END)

        if not result['en_content'] and not result['ch_content']:
            self.content_text.insert(tk.END, "未生成任何邮件内容")
            self.btn_copy.config(state='disabled')
            return

        self.content_text.insert(tk.END, "===== 英文内容 =====\n")
        self.content_text.insert(tk.END, result['en_content'] + "\n\n")
        self.content_text.insert(tk.END, "===== 中文内容 =====\n")
        self.content_text.insert(tk.END, result['ch_content'])
        self.btn_copy.config(state='normal')

    def on_history_select(self, event):
        """选择历史记录时显示相应内容"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if 0 <= index < len(self.history):
            self.display_content(self.history[index])

    def copy_content(self):
        """复制当前显示的邮件内容到剪贴板"""
        content = self.content_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("提示", "内容已复制到剪贴板")