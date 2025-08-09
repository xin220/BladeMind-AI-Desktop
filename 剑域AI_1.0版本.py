import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from PIL import Image, ImageTk
import os
import sys

class DeepSeekClone:
    def __init__(self, root):
        self.root = root
        self.root.title("剑域AI-1.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1f22")
        
        # 设置深色模式主题
        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure('.', background="#1e1f22", foreground="white")
        self.style.configure('TFrame', background="#1e1f22")
        self.style.configure('TLabel', background="#1e1f22", foreground="white")
        self.style.configure('TButton', 
                            background="#2b2d31", 
                            foreground="white",
                            borderwidth=1,
                            focusthickness=3,
                            focuscolor="#2b2d31")
        self.style.map('TButton', 
                       background=[('active', '#3a3d44')],
                       foreground=[('active', 'white')])
        
        # 左侧功能栏
        self.sidebar = ttk.Frame(root, width=50, padding=10)
        self.sidebar.pack(side="left", fill="y")
        
        # 顶部标题
        self.header = ttk.Frame(root, height=50, padding=10)
        self.header.pack(side="top", fill="x")
        self.title_label = ttk.Label(self.header, text="新对话", font=("Arial", 14, "bold"))
        self.title_label.pack(side="left")
        
        # 聊天区域
        self.chat_frame = ttk.Frame(root)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.chat_canvas = tk.Canvas(self.chat_frame, bg="#2b2d31", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_container = ttk.Frame(self.chat_canvas)
        
        self.chat_container.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        self.chat_canvas.create_window((0, 0), window=self.chat_container, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        
        # 初始欢迎消息
        self.add_welcome_message()
        
        # 底部输入区域
        self.input_frame = ttk.Frame(root, padding=10)
        self.input_frame.pack(side="bottom", fill="x")
        
        # 底部按钮
        self.btn_frame = ttk.Frame(self.input_frame)
        self.btn_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.deep_think_btn = ttk.Button(self.btn_frame, text="深度思考(R1)", width=13)
        self.deep_think_btn.pack(side="top", pady=(0, 5))
        
        self.search_btn = ttk.Button(self.btn_frame, text="联网搜索")
        self.search_btn.pack(side="top")
        
        # 输入控件
        self.input_controls = ttk.Frame(self.input_frame)
        self.input_controls.pack(side="left", fill="x", expand=True)
        
        self.entry = tk.Text(self.input_controls, height=3, bg="#2b2d31", fg="white", 
                            insertbackground="white", relief="flat", highlightthickness=1,
                            highlightbackground="#3c3f45", highlightcolor="#3c3f45")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.insert("1.0", "给剑域AI_1.0发送消息")
        self.entry.bind("<FocusIn>", self.clear_placeholder)
        self.entry.bind("<Return>", self.on_enter_pressed)
        
        # 附件按钮
        self.attach_btn = ttk.Button(self.input_controls, text="📎", width=2, 
                                    command=self.show_attachment_dialog)
        self.attach_btn.pack(side="left", padx=(0, 5))
        
        # 刷新按钮（初始隐藏）
        self.refresh_btn = ttk.Button(self.input_controls, text="🔄", width=2,
                                     command=self.show_network_error)
        self.refresh_btn.pack(side="left", padx=(0, 5))
        self.refresh_btn.pack_forget()
        
        # 发送按钮
        self.send_btn = ttk.Button(self.input_controls, text="↑", width=2, command=self.send_message)
        self.send_btn.pack(side="left")
        
        # 开启新对话按钮
        self.new_chat_btn = ttk.Button(self.input_frame, text="开启新对话", 
                                      command=self.start_new_chat, style="TButton")
        self.new_chat_btn.pack(side="right", fill="y")
        
        # 状态变量
        self.thinking = False
        self.network_error = False
    
    def add_welcome_message(self):
        welcome_frame = ttk.Frame(self.chat_container, padding=(15, 10), relief="flat")
        welcome_frame.pack(fill="x", pady=(10, 5), padx=20, anchor="w")
        
        welcome_label = ttk.Label(
            welcome_frame,
            text="我是剑域AI-1.0，很高兴见到你!\n我可以帮你写代码、读文件、写作各种创意内容，请把你的任务交给我吧~",
            justify="left",
            font=("Arial", 11)
        )
        welcome_label.pack(anchor="w")
        
        self.chat_canvas.yview_moveto(1.0)
    
    def clear_placeholder(self, event):
        if self.entry.get("1.0", "end-1c") == "给DeepSeek发送消息":
            self.entry.delete("1.0", "end")
    
    def on_enter_pressed(self, event):
        if not event.state & 0x1:  # 检查是否按下了Shift键
            self.send_message()
            return "break"  # 防止默认换行
        return None
    
    def send_message(self):
        message = self.entry.get("1.0", "end-1c").strip()
        if not message or message == "给DeepSeek发送消息":
            return
        
        # 添加用户消息
        self.add_user_message(message)
        self.entry.delete("1.0", "end")
        
        # 模拟AI思考
        self.simulate_thinking()
    
    def add_user_message(self, message):
        message_frame = ttk.Frame(self.chat_container, padding=(15, 10), relief="flat")
        message_frame.pack(fill="x", pady=5, padx=(100, 20), anchor="e")
        
        message_label = ttk.Label(
            message_frame,
            text=message,
            justify="right",
            wraplength=400,
            background="#45494e",
            foreground="white",
            padding=10,
            borderwidth=0,
            relief="flat",
            font=("Arial", 11)
        )
        message_label.pack(anchor="e")
        
        self.chat_canvas.yview_moveto(1.0)
    
    def simulate_thinking(self):
        if self.thinking:
            return
        
        self.thinking = True
        
        # 添加思考消息
        thinking_frame = ttk.Frame(self.chat_container, padding=(15, 10), relief="flat")
        thinking_frame.pack(fill="x", pady=5, padx=20, anchor="w")
        
        # 加载指示器
        loading_label = ttk.Label(
            thinking_frame,
            text="正在思考...",
            justify="left",
            font=("Arial", 11)
        )
        loading_label.pack(anchor="w")
        
        # 更新画布滚动位置
        self.chat_canvas.yview_moveto(1.0)
        
        # 在单独的线程中模拟长时间运行的任务
        threading.Thread(target=self.simulate_ai_response, args=(loading_label, thinking_frame), daemon=True).start()
    
    def simulate_ai_response(self, loading_label, frame):
        # 模拟思考时间
        time.sleep(1.5)
        
        # 更新UI需要在主线程中完成
        self.root.after(0, self.show_error_message, loading_label, frame)
    
    def show_error_message(self, loading_label, frame):
        self.thinking = False
        self.network_error = True
        self.refresh_btn.pack(side="left", padx=(0, 5))  # 显示刷新按钮
        
        # 删除加载消息并添加错误消息
        loading_label.destroy()
        
        error_label = ttk.Label(
            frame,
            text="服务器繁忙，请稍后再试...",
            justify="left",
            background="#2b2d31",
            foreground="white",
            padding=10,
            font=("Arial", 11)
        )
        error_label.pack(anchor="w")
        
        # 添加状态图标
        status_frame = ttk.Frame(frame)
        status_frame.pack(anchor="w", pady=(5, 0))
        
        # 图标使用文本替代
        for icon, tooltip in [("📋", "复制"), ("🔄", "重新生成"), ("👍", "赞"), ("👎", "踩")]:
            btn = ttk.Button(status_frame, text=icon, width=2)
            btn.pack(side="left", padx=2)
        
        self.chat_canvas.yview_moveto(1.0)
    
    def show_attachment_dialog(self):
        filename = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[("所有文件", "*.*")]
        )
        
        if filename:
            # 添加用户消息显示上传
            self.add_upload_message(filename)
            
            # 模拟上传过程
            threading.Thread(target=self.simulate_upload, args=(filename,), daemon=True).start()
    
    def add_upload_message(self, filename):
        short_name = os.path.basename(filename)[:20] + (os.path.basename(filename)[20:] and '...')
        
        message_frame = ttk.Frame(self.chat_container, padding=(15, 10), relief="flat")
        message_frame.pack(fill="x", pady=5, padx=(100, 20), anchor="e")
        
        message_label = ttk.Label(
            message_frame,
            text=f"上传文件: {short_name}",
            justify="right",
            background="#45494e",
            foreground="white",
            padding=10,
            font=("Arial", 11)
        )
        message_label.pack(anchor="e")
        
        # 添加加载指示器
        loading_frame = ttk.Frame(message_frame)
        loading_frame.pack(anchor="e")
        
        loading_label = ttk.Label(
            loading_frame,
            text="◌ 上传中...",
            foreground="#a0a0a0",
            font=("Arial", 9)
        )
        loading_label.pack(anchor="e")
        
        self.chat_canvas.yview_moveto(1.0)
        
        return loading_label
    
    def simulate_upload(self, filename):
        # 模拟上传时间
        time.sleep(1.5)
        
        # 更新UI需要在主线程中完成
        self.root.after(0, self.finish_upload_simulation, filename)
    
    def finish_upload_simulation(self, filename):
        # 在实际应用中，这里会更新上传完成状态
        self.chat_canvas.yview_moveto(1.0)
    
    def show_network_error(self):
        messagebox.showinfo("网络错误", "当前无网络连接")
    
    def start_new_chat(self):
        # 清除当前所有聊天
        for widget in self.chat_container.winfo_children():
            widget.destroy()
        
        # 重置状态
        self.thinking = False
        self.network_error = False
        self.refresh_btn.pack_forget()
        
        # 添加欢迎消息
        self.add_welcome_message()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeepSeekClone(root)
    
    # 添加底部提示文字
    hint_label = ttk.Label(
        root, 
        text="内容由AI生成，请仔细甄别",
        foreground="#8e8e93",
        font=("Arial", 9)
    )
    hint_label.pack(side="bottom", fill="x", pady=5)
    
    root.mainloop()
