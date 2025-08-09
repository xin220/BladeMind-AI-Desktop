import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import datetime
from PIL import Image, ImageTk, ImageDraw

def create_rounded_rectangle(width, height, radius, color):
    """创建圆角矩形图像"""
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(0, 0), (width, height)], radius, fill=color)
    return ImageTk.PhotoImage(image)

class DeepSeekClone:
    def __init__(self, root):
        self.root = root
        self.root.title("剑域AI-1.0")
        self.root.geometry("900x700")
        self.root.configure(bg="#111418")
        
        # 创建自定义圆角图像
        self.bg_colors = {
            "primary": "#1c2a44",
            "user_bubble": "#0067C0",
            "ai_bubble": "#252D38",
            "error_bubble": "#3A2323",
            "input": "#1A2029",
            "button": "#1E2A3D",
            "button_hover": "#2A3B56",
            "button_active": "#27ae60",  # 绿色激活状态
            "button_pressed": "#219653",  # 绿色按下状态
            "scrollbar": "#3c4a65"
        }
        
        self.rounded_bg = {
            "user": create_rounded_rectangle(500, 100, 15, self.bg_colors["user_bubble"]),
            "ai": create_rounded_rectangle(500, 100, 15, self.bg_colors["ai_bubble"]),
            "error": create_rounded_rectangle(500, 100, 15, self.bg_colors["error_bubble"]),
            "input": create_rounded_rectangle(800, 80, 10, self.bg_colors["input"])
        }
        
        # 字体设置
        self.title_font = ("Microsoft YaHei UI", 16, "bold")
        self.message_font = ("Microsoft YaHei UI", 12)
        self.button_font = ("Microsoft YaHei UI", 11, "bold")
        self.small_font = ("Microsoft YaHei UI", 10)
        self.timestamp_font = ("Microsoft YaHei UI", 9)
        
        # 创建主框架
        self.main_frame = tk.Frame(root, bg="#111418")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 顶部标题栏
        header_frame = tk.Frame(self.main_frame, bg="#111418", height=60)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # 左侧标题
        title_label = tk.Label(
            header_frame,
            text="剑域AI-1.0",
            font=self.title_font,
            fg="#3498DB",
            bg="#111418",
            padx=10
        )
        title_label.pack(side="left")
        
        # 右侧新对话按钮
        self.new_chat_btn = tk.Button(
            header_frame,
            text="新对话",
            font=self.button_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_hover"],
            bd=0,
            padx=20,
            pady=8,
            command=self.start_new_chat
        )
        self.new_chat_btn.pack(side="right", padx=10)
        
        # 聊天区域
        chat_container = tk.Frame(self.main_frame, bg="#111418")
        chat_container.pack(fill="both", expand=True)
        
        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(chat_container, bg="#151A21", highlightthickness=0)
        
        # 创建自定义滚动条
        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar", 
                        background=self.bg_colors["scrollbar"],
                        troughcolor="#111418",
                        arrowsize=15,
                        width=15)
        
        self.scrollbar = ttk.Scrollbar(
            chat_container, 
            orient="vertical", 
            command=self.canvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        
        self.chat_frame = tk.Frame(self.canvas, bg="#151A21")
        
        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # 添加初始聊天内容
        self.add_welcome_message()
        self.add_user_message("你好，我是你爹")
        self.add_ai_error_message()
        self.add_user_message("呜呜呜，逆子！竟然不理爹！")
        self.add_ai_error_message()
        
        # 滚动到最新消息
        self.scroll_to_bottom()
        
        # 底部控制面板
        control_frame = tk.Frame(self.main_frame, bg="#111418", height=150)
        control_frame.pack(fill="x", pady=(15, 10))
        
        # 功能按钮区域
        btn_frame = tk.Frame(control_frame, bg="#111418")
        btn_frame.pack(side="left", fill="y", padx=(0, 15))
        
        # 深度思考按钮
        self.deep_think_btn = tk.Button(
            btn_frame,
            text="深度思考(R1)",
            font=self.button_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_pressed"],
            bd=0,
            padx=10,
            pady=6,
            command=self.toggle_deep_think
        )
        self.deep_think_btn.pack(side="top", pady=(0, 10))
        
        # 联网搜索按钮
        self.search_btn = tk.Button(
            btn_frame,
            text="联网搜索",
            font=self.button_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_pressed"],
            bd=0,
            padx=10,
            pady=6,
            command=self.toggle_search
        )
        self.search_btn.pack(side="top")
        
        # 输入区域
        input_container = tk.Frame(control_frame, bg="#111418")
        input_container.pack(side="left", fill="both", expand=True)
        
        # 输入框背景
        input_bg = tk.Label(input_container, image=self.rounded_bg["input"], bg="#111418")
        input_bg.pack(fill="both", expand=True)
        input_bg.image = self.rounded_bg["input"]
        
        # 实际输入框
        self.entry = tk.Text(
            input_bg,
            height=3,
            bg=self.bg_colors["input"],
            fg="#E0E0E0",
            insertbackground="#E0E0E0",
            relief="flat",
            highlightthickness=0,
            font=self.message_font,
            padx=20,
            pady=15,
            wrap="word"
        )
        self.entry.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)
        self.entry.insert("1.0", "给剑域AI发送消息")
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<Return>", self.on_enter_pressed)
        
        # 按钮容器
        btn_container = tk.Frame(input_container, bg="#111418")
        btn_container.pack(side="right", fill="y", padx=(10, 0))
        
        # 附件按钮
        self.attach_btn = tk.Button(
            btn_container,
            text="📎 附件",
            font=self.button_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_hover"],
            bd=0,
            padx=10,
            pady=5,
            command=self.show_attachment_dialog
        )
        self.attach_btn.pack(side="top", pady=(0, 5))
        
        # 刷新按钮
        self.refresh_btn = tk.Button(
            btn_container,
            text="🔄 刷新",
            font=self.button_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_hover"],
            bd=0,
            padx=10,
            pady=5,
            command=self.show_network_error
        )
        self.refresh_btn.pack(side="top", pady=5)
        
        # 发送按钮
        self.send_btn = tk.Button(
            btn_container,
            text="↑ 发送",
            font=self.button_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button_active"],
            activebackground="#0090FF",
            bd=0,
            padx=10,
            pady=5,
            command=self.send_message
        )
        self.send_btn.pack(side="top")
        
        # 底部状态栏
        footer_frame = tk.Frame(self.main_frame, bg="#111418", height=40)
        footer_frame.pack(fill="x", pady=(5, 0))
        
        # 查看日志按钮
        self.logs_btn = tk.Button(
            footer_frame,
            text="查看日志",
            font=self.small_font,
            fg="#95A5A6",
            bg="#111418",
            activebackground="#1A2029",
            bd=0,
            padx=10,
            command=self.view_logs
        )
        self.logs_btn.pack(side="left", padx=(10, 0))
        
        # 状态消息
        status_label = tk.Label(
            footer_frame,
            text="内容由AI生成，请仔细甄别",
            font=self.small_font,
            fg="#95A5A6",
            bg="#111418",
            padx=10
        )
        status_label.pack(side="right")
        
        # 状态变量
        self.thinking = False
        self.deep_think_active = False
        self.search_active = False
        self.thinking_messages = {}
        self.upload_status_labels = {}
        self.active_threads = []
        
        # 鼠标悬停效果
        self.setup_hover_effects()

    def setup_hover_effects(self):
        """设置按钮的悬停效果"""
        buttons = [
            self.new_chat_btn, self.deep_think_btn, self.search_btn,
            self.attach_btn, self.refresh_btn, self.logs_btn, self.send_btn
        ]
        
        for btn in buttons:
            if hasattr(btn, 'config'):
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.bg_colors["button_hover"]))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.bg_colors["button"]))
        
        # 特殊处理发送按钮
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg="#0090FF"))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=self.bg_colors["button_active"]))

    def add_welcome_message(self):
        """添加欢迎消息"""
        frame = tk.Frame(self.chat_frame, bg="#151A21")
        frame.pack(fill="x", pady=(20, 10), padx=20)
        
        # 欢迎消息内容
        content_frame = tk.Frame(frame, bg=self.bg_colors["ai_bubble"])
        content_frame.pack(fill="x", pady=5)
        
        message = (
            "我是剑域AI-1.0，很高兴见到你!\n"
            "我可以帮你写代码、读文件、写作各种创意内容，请把你的任务交给我吧~"
        )
        label = tk.Label(
            content_frame,
            text=message,
            font=self.message_font,
            fg="#E0E0E0",
            bg=self.bg_colors["ai_bubble"],
            justify="left",
            padx=20,
            pady=15,
            wraplength=550
        )
        label.pack(anchor="w")
        
        # 时间戳
        timestamp = tk.Label(
            frame,
            text=datetime.datetime.now().strftime("%H:%M"),
            font=self.timestamp_font,
            fg="#7F8C8D",
            bg="#151A21"
        )
        timestamp.pack(anchor="w", padx=25)
        
        self.scroll_to_bottom()
        return frame

    def add_user_message(self, message_text):
        """添加用户消息"""
        frame = tk.Frame(self.chat_frame, bg="#151A21")
        frame.pack(fill="x", pady=(20, 10), padx=20)
        
        # 内容区域
        content_frame = tk.Frame(frame, bg=self.bg_colors["user_bubble"])
        content_frame.pack(side="right", anchor="e", padx=(150, 0))
        
        label = tk.Label(
            content_frame,
            text=message_text,
            font=self.message_font,
            fg="#FFFFFF",
            bg=self.bg_colors["user_bubble"],
            justify="right",
            padx=20,
            pady=15,
            wraplength=400
        )
        label.pack(anchor="e")
        
        # 时间戳
        timestamp = tk.Label(
            frame,
            text=datetime.datetime.now().strftime("%H:%M"),
            font=self.timestamp_font,
            fg="#7F8C8D",
            bg="#151A21"
        )
        timestamp.pack(side="right", padx=25)
        
        self.scroll_to_bottom()
        return frame

    def add_ai_error_message(self):
        """添加AI错误消息"""
        frame = tk.Frame(self.chat_frame, bg="#151A21")
        frame.pack(fill="x", pady=(20, 10), padx=20)
        
        # 内容区域
        content_frame = tk.Frame(frame, bg=self.bg_colors["error_bubble"])
        content_frame.pack(side="left", anchor="w", padx=(0, 150))
        
        # 错误消息
        error_label = tk.Label(
            content_frame,
            text="服务器繁忙，请稍后再试...",
            font=self.message_font,
            fg="#E74C3C",
            bg=self.bg_colors["error_bubble"],
            justify="left",
            padx=20,
            pady=10,
            wraplength=450
        )
        error_label.pack(anchor="w")
        
        # 操作按钮区域
        btn_frame = tk.Frame(content_frame, bg=self.bg_colors["error_bubble"])
        btn_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        # 复制按钮
        copy_btn = tk.Button(
            btn_frame,
            text="复制",
            font=self.small_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_hover"],
            bd=0,
            padx=12,
            pady=4,
            command=lambda: self.copy_to_clipboard("服务器繁忙，请稍后再试...")
        )
        copy_btn.pack(side="left", padx=(0, 10))
        copy_btn.bind("<Enter>", lambda e: copy_btn.config(bg=self.bg_colors["button_hover"]))
        copy_btn.bind("<Leave>", lambda e: copy_btn.config(bg=self.bg_colors["button"]))
        
        # 重新生成按钮
        regen_btn = tk.Button(
            btn_frame,
            text="重新生成",
            font=self.small_font,
            fg="#FFFFFF",
            bg=self.bg_colors["button"],
            activebackground=self.bg_colors["button_hover"],
            bd=0,
            padx=12,
            pady=4,
            command=self.regenerate_response
        )
        regen_btn.pack(side="left")
        regen_btn.bind("<Enter>", lambda e: regen_btn.config(bg=self.bg_colors["button_hover"]))
        regen_btn.bind("<Leave>", lambda e: regen_btn.config(bg=self.bg_colors["button"]))
        
        # 时间戳
        timestamp = tk.Label(
            frame,
            text=datetime.datetime.now().strftime("%H:%M"),
            font=self.timestamp_font,
            fg="#7F8C8D",
            bg="#151A21"
        )
        timestamp.pack(side="left", padx=25)
        
        self.scroll_to_bottom()
        return frame

    def add_thinking_message(self):
        """添加思考中消息"""
        frame = tk.Frame(self.chat_frame, bg="#151A21")
        frame.pack(fill="x", pady=(20, 10), padx=20)
        
        # 内容区域
        content_frame = tk.Frame(frame, bg=self.bg_colors["ai_bubble"])
        content_frame.pack(side="left", anchor="w", padx=(0, 150))
        
        # 思考指示器和文本
        loading_frame = tk.Frame(content_frame, bg=self.bg_colors["ai_bubble"])
        loading_frame.pack(fill="x", padx=20, pady=15)
        
        # 动态加载点
        self.loading_label = tk.Label(
            loading_frame,
            text="正在思考...",
            font=self.message_font,
            fg="#95A5A6",
            bg=self.bg_colors["ai_bubble"],
            justify="left",
        )
        self.loading_label.pack(anchor="w")
        
        # 保存消息引用
        self.thinking_messages[frame] = {
            "frame": frame,
            "content": content_frame
        }
        
        # 开始加载动画
        self.animate_loading()
        
        self.scroll_to_bottom()
        return frame

    def animate_loading(self):
        """动画显示思考过程"""
        if not hasattr(self, 'loading_stage'):
            self.loading_stage = 0
            
        dots = "." * (self.loading_stage % 4)
        self.loading_label.config(text=f"正在思考{dots}")
        self.loading_stage += 1
        
        # 如果还有思考消息，继续动画
        if hasattr(self, 'thinking_timer') and self.thinking_timer:
            self.root.after(500, self.animate_loading)

    def clear_placeholder(self, event):
        """清除输入框占位符"""
        if self.entry.get("1.0", "end-1c") == "给剑域AI发送消息":
            self.entry.delete("1.0", "end")

    def on_enter_pressed(self, event):
        """处理Enter键发送消息"""
        if not event.state & 0x1:  # 检查是否按下了Shift键
            self.send_message()
            return "break"  # 防止默认换行
        return None

    def send_message(self):
        """发送消息"""
        message = self.entry.get("1.0", "end-1c").strip()
        if not message or message == "给剑域AI发送消息":
            return
        
        # 添加用户消息
        self.add_user_message(message)
        self.entry.delete("1.0", "end")
        
        # 确保滚动到底部
        self.scroll_to_bottom()
        
        # 添加思考消息
        thinking_frame = self.add_thinking_message()
        
        # 开始思考计时器
        self.thinking_timer = True
        self.animate_loading()
        
        # 在单独的线程中模拟思考过程
        thinking_time = 3 if self.deep_think_active else 2
        thread = threading.Thread(target=self.simulate_thinking, args=(thinking_frame, thinking_time), daemon=True)
        thread.start()
        self.active_threads.append(thread)

    def simulate_thinking(self, frame, thinking_time):
        """模拟AI思考过程"""
        try:
            time.sleep(thinking_time)
            
            # 更新UI需要在主线程中完成
            self.root.after(0, self.show_error_message, frame)
            
            # 滚动到底部显示结果
            self.root.after(10, self.scroll_to_bottom)
        except Exception as e:
            print(f"思考线程错误: {e}")

    def show_error_message(self, frame):
        """显示错误消息"""
        try:
            # 停止动画
            self.thinking_timer = False
            
            # 删除加载消息
            if frame in self.thinking_messages:
                content_frame = self.thinking_messages[frame]["content"]
                
                # 移除原有内容
                for widget in content_frame.winfo_children():
                    widget.destroy()
                
                # 添加错误消息
                error_label = tk.Label(
                    content_frame,
                    text="服务器繁忙，请稍后再试...",
                    font=self.message_font,
                    fg="#E74C3C",
                    bg=self.bg_colors["error_bubble"],
                    justify="left",
                    padx=20,
                    pady=10,
                    wraplength=450
                )
                error_label.pack(anchor="w")
                
                # 操作按钮区域
                btn_frame = tk.Frame(content_frame, bg=self.bg_colors["error_bubble"])
                btn_frame.pack(fill="x", padx=20, pady=(5, 10))
                
                # 复制按钮
                copy_btn = tk.Button(
                    btn_frame,
                    text="复制",
                    font=self.small_font,
                    fg="#FFFFFF",bg=self.bg_colors["button"],
                    activebackground=self.bg_colors["button_hover"],
                    bd=0,
                    padx=12,
                    pady=4,
                    command=lambda: self.copy_to_clipboard("服务器繁忙，请稍后再试...")
                )
                copy_btn.pack(side="left", padx=(0, 10))
                copy_btn.bind("<Enter>", lambda e: copy_btn.config(bg=self.bg_colors["button_hover"]))
                copy_btn.bind("<Leave>", lambda e: copy_btn.config(bg=self.bg_colors["button"]))
                
                # 重新生成按钮
                regen_btn = tk.Button(
                    btn_frame,
                    text="重新生成",
                    font=self.small_font,
                    fg="#FFFFFF",
                    bg=self.bg_colors["button"],
                    activebackground=self.bg_colors["button_hover"],
                    bd=0,
                    padx=12,
                    pady=4,
                    command=self.regenerate_response
                )
                regen_btn.pack(side="left")
                regen_btn.bind("<Enter>", lambda e: regen_btn.config(bg=self.bg_colors["button_hover"]))
                regen_btn.bind("<Leave>", lambda e: regen_btn.config(bg=self.bg_colors["button"]))
                
                # 删除思考消息引用
                del self.thinking_messages[frame]
        except Exception as e:
            print(f"显示错误消息时出错: {e}")

    def copy_to_clipboard(self, text):
        """复制到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("复制成功", "内容已复制到剪贴板")
        except Exception as e:
            print(f"复制到剪贴板时出错: {e}")

    def regenerate_response(self):
        """重新生成响应"""
        try:
            messagebox.showinfo("重新生成", "正在尝试重新获取响应...")
        except Exception as e:
            print(f"重新生成响应时出错: {e}")

    def show_attachment_dialog(self):
        """显示附件选择对话框"""
        try:
            filename = filedialog.askopenfilename(
                title="选择文件",
                filetypes=[("所有文件", "*.*")]
            )
            
            if filename:
                loading_label = self.add_upload_message(filename)
                threading.Thread(target=self.simulate_upload, args=(filename, loading_label), daemon=True).start()
        except Exception as e:
            print(f"显示附件对话框时出错: {e}")

    def add_upload_message(self, filename):
        """添加上传文件消息"""
        try:
            short_name = os.path.basename(filename)
            if len(short_name) > 20:
                short_name = short_name[:17] + "..."
            
            frame = tk.Frame(self.chat_frame, bg="#151A21")
            frame.pack(fill="x", pady=(20, 10), padx=20)
            
            content_frame = tk.Frame(frame, bg=self.bg_colors["user_bubble"])
            content_frame.pack(side="right", anchor="e", padx=(150, 0))
            
            label = tk.Label(
                content_frame,
                text=f"上传文件: {short_name}",
                font=self.message_font,
                fg="#FFFFFF",
                bg=self.bg_colors["user_bubble"],
                justify="right",
                padx=20,
                pady=10,
                wraplength=300
            )
            label.pack(anchor="e")
            
            loading_label = tk.Label(
                content_frame,
                text="◌◌ 上传中...",
                font=self.small_font,
                fg="#D0D0D0",
                bg=self.bg_colors["user_bubble"],
                padx=20,
                pady=(0, 10)
            )
            loading_label.pack(anchor="e")
            
            timestamp = tk.Label(
                frame,
                text=datetime.datetime.now().strftime("%H:%M"),
                font=self.timestamp_font,
                fg="#7F8C8D",
                bg="#151A21"
            )
            timestamp.pack(side="right", padx=25)
            
            self.scroll_to_bottom()
            return loading_label
        except Exception as e:
            print(f"添加上传消息时出错: {e}")
            return None

    def simulate_upload(self, filename, loading_label):
        """模拟文件上传过程"""
        try:
            for i in range(5):
                time.sleep(0.3)
                self.root.after(0, lambda l=loading_label, s=f"◌◌ 上传中{'.'*(i+1)}": l.config(text=s))
            
            self.root.after(0, lambda: self.finish_upload_simulation(loading_label))
        except Exception as e:
            print(f"模拟上传时出错: {e}")

    def finish_upload_simulation(self, loading_label):
        """完成文件上传模拟"""
        try:
            loading_label.config(text="✓ 上传完成")
        except Exception as e:
            print(f"完成上传模拟时出错: {e}")

    def show_network_error(self):
        """显示网络错误提示"""
        try:
            messagebox.showinfo("网络错误", "当前无网络连接")
        except Exception as e:
            print(f"显示网络错误时出错: {e}")

    def view_logs(self):
        """查看日志功能"""
        try:
            messagebox.showinfo("查看日志", "日志功能尚未实现")
        except Exception as e:
            print(f"查看日志时出错: {e}")

    def start_new_chat(self):
        """开始新对话"""
        try:
            # 清除当前所有聊天
            for widget in self.chat_frame.winfo_children():
                widget.destroy()
            
            # 重置状态
            self.thinking = False
            self.deep_think_active = False
            self.search_active = False
            self.thinking_messages = {}
            
            # 重置按钮状态
            self.deep_think_btn.config(bg=self.bg_colors["button"])
            self.search_btn.config(bg=self.bg_colors["button"])
            
            # 添加欢迎消息
            self.add_welcome_message()
            # 滚动到顶部显示欢迎消息
            self.scroll_to_top()
        except Exception as e:
            print(f"开始新对话时出错: {e}")

    def toggle_deep_think(self):
        """切换深度思考模式"""
        try:
            self.deep_think_active = not self.deep_think_active
            color = self.bg_colors["button_active"] if self.deep_think_active else self.bg_colors["button"]
            self.deep_think_btn.config(bg=color)
            
            status = "已激活" if self.deep_think_active else "已关闭"
            messagebox.showinfo("深度思考", f"深度思考模式{status}")
            
            # 绿色激活效果
            self.root.after(100, lambda: self.deep_think_btn.config(bg=self.bg_colors["button_pressed"]))
            self.root.after(500, lambda: self.deep_think_btn.config(
                bg=self.bg_colors["button_active"] if self.deep_think_active else self.bg_colors["button"]
            ))
        except Exception as e:
            print(f"切换深度思考模式时出错: {e}")

    def toggle_search(self):
        """切换联网搜索模式"""
        try:
            self.search_active = not self.search_active
            color = self.bg_colors["button_active"] if self.search_active else self.bg_colors["button"]
            self.search_btn.config(bg=color)
            
            status = "已激活" if self.search_active else "已关闭"
            messagebox.showinfo("联网搜索", f"联网搜索模式{status}")
            
            # 绿色激活效果
            self.root.after(100, lambda: self.search_btn.config(bg=self.bg_colors["button_pressed"]))
            self.root.after(500, lambda: self.search_btn.config(
                bg=self.bg_colors["button_active"] if self.search_active else self.bg_colors["button"]
            ))
        except Exception as e:
            print(f"切换联网搜索模式时出错: {e}")

    def scroll_to_bottom(self):
        """滚动到聊天区域底部"""
        try:
            self.canvas.yview_moveto(1.0)
            self.root.update_idletasks()
        except Exception as e:
            print(f"滚动到底部时出错: {e}")

    def scroll_to_top(self):
        """滚动到聊天区域顶部"""
        try:
            self.canvas.yview_moveto(0.0)
            self.root.update_idletasks()
        except Exception as e:
            print(f"滚动到顶部时出错: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    
    try:
        # 设置窗口图标
        root.iconbitmap(default=None)
    except:
        pass
    
    # 设置窗口最小尺寸
    root.minsize(800, 600)
    
    app = DeepSeekClone(root)
    root.mainloop()
