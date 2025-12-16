import customtkinter as ctk
import tkinter as tk
import threading
import json
import datetime
from tkinter import messagebox

# 引入项目其他模块
from src.config import (
    COLOR_ORANGE,
    COLOR_BLUE,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_RED,
    TEXT_BLACK,
    TEXT_WHITE,
)
from src.ui.widgets import KeyValueTable
from src.ui.popups import ImagePopup, CurlImportDialog
from src.core.network import send_http_request
from src.core.converters import generate_curl_command
from src.data.storage import load_collections, save_collections, append_log_to_file


class APITesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern API Tester Modular")
        self.geometry("1080x750")

        # === 状态变量 ===
        self.logs = []  # 内存中的运行日志
        self.collections = load_collections()  # 从文件加载收藏
        self.sidebar_visible = True
        self.sidebar_width = 200  # 侧边栏宽度

        self.search_matches = []
        self.current_match_index = -1

        # === 布局配置 ===
        self.grid_columnconfigure(0, weight=0)  # 侧边栏列
        self.grid_columnconfigure(1, weight=1)  # 主内容列
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        # 1. 侧边栏
        self.sidebar_frame = ctk.CTkFrame(
            self, width=self.sidebar_width, corner_radius=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.setup_sidebar_content()

        # 2. 主操作区
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(
            1, weight=1
        )  # 0是TopBar, 1是Tabs, 2是Response(但在setup里是用pack/grid混用，详见下面)

        # 这里我们重新规划 Main Area 的内部布局
        # Top Bar (Method/URL)
        self.setup_top_bar()
        # Request Tabs (Params/Body etc)
        self.setup_request_tabs()
        # Response Area
        self.setup_response_area()

    # =========================================
    # 侧边栏逻辑 (Sidebar)
    # =========================================
    def setup_sidebar_content(self):
        self.side_tabs = ctk.CTkTabview(self.sidebar_frame)
        self.side_tabs.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_col = self.side_tabs.add("Saved")
        self.tab_hist = self.side_tabs.add("History")

        # --- Collections Tab ---
        self.col_scroll = ctk.CTkScrollableFrame(self.tab_col, fg_color="transparent")
        self.col_scroll.pack(fill="both", expand=True, pady=5)
        self.refresh_collections_ui()

        # --- History Tab ---
        ctk.CTkButton(
            self.tab_hist,
            text="Clear History",
            text_color=TEXT_BLACK,
            height=24,
            fg_color=COLOR_GRAY,
            command=self.clear_history,
        ).pack(fill="x", pady=2)

        self.hist_scroll = ctk.CTkScrollableFrame(self.tab_hist, fg_color="transparent")
        self.hist_scroll.pack(fill="both", expand=True, pady=5)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_frame.grid_forget()
            self.sidebar_visible = False
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.sidebar_visible = True

    def refresh_collections_ui(self):
        for w in self.col_scroll.winfo_children():
            w.destroy()

        for idx, item in enumerate(self.collections):
            btn = ctk.CTkButton(
                self.col_scroll,
                text=f"{item.get('name', 'Untitled')}\n{item.get('url')[:30]}...",
                anchor="w",
                width=120,
                height=40,
                text_color=TEXT_BLACK,
                fg_color="transparent",
                border_width=1,
                border_color="gray",
                command=lambda i=idx: self.load_collection_item(i),
            )
            btn.pack(fill="x", pady=2)
            # 绑定右键菜单
            btn.bind(
                "<Button-3>",
                lambda event, i=idx: self.create_collection_context_menu(event, i),
            )

    def create_collection_context_menu(self, event, index):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Load", command=lambda: self.load_collection_item(index))
        menu.add_command(
            label="Delete", command=lambda: self.delete_collection_item_by_index(index)
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def refresh_history_ui(self):
        for w in self.hist_scroll.winfo_children():
            w.destroy()

        for idx, item in enumerate(self.logs):
            status = item["status"]
            # 简单的状态颜色指示
            color = COLOR_GREEN if str(status).startswith("2") else COLOR_RED
            if str(status) == "ERROR":
                color = COLOR_RED

            btn_text = f"[{item['time']}] {item['method']} {item['status']}\n{item['url'][:25]}..."

            btn = ctk.CTkButton(
                self.hist_scroll,
                text=btn_text,
                anchor="w",
                height=40,
                fg_color="transparent",
                border_width=1,
                border_color="#444",
                text_color=("black", "#CCC"),
                hover_color="#333",
                command=lambda i=idx: self.load_history_item(i),
            )
            # 添加状态小圆点
            status_indicator = ctk.CTkLabel(
                btn, text="●", text_color=color, font=("Arial", 10)
            )
            status_indicator.place(relx=0.9, rely=0.1, anchor="ne")
            btn.pack(fill="x", pady=2)

    # =========================================
    # 顶部栏逻辑 (Top Bar)
    # =========================================
    def setup_top_bar(self):
        top_frame = ctk.CTkFrame(self.main_area)
        top_frame.pack(fill="x", pady=(0, 10))

        # 汉堡菜单按钮
        ctk.CTkButton(
            top_frame,
            text="☰",
            width=30,
            fg_color="transparent",
            border_width=1,
            text_color=("black", "white"),
            command=self.toggle_sidebar,
        ).pack(side="left", padx=5, pady=5)

        # 请求方法
        self.method_var = ctk.StringVar(value="GET")
        ctk.CTkComboBox(
            top_frame,
            values=["GET", "POST", "PUT", "DELETE", "PATCH"],
            variable=self.method_var,
            width=80,
        ).pack(side="left", padx=5)

        # URL 输入框
        self.url_entry = ctk.CTkEntry(
            top_frame, placeholder_text="https://api.example.com"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.url_entry.bind("<Return>", lambda e: self.start_request_thread())

        # 发送按钮
        self.send_btn = ctk.CTkButton(
            top_frame,
            text="Send",
            text_color=TEXT_WHITE,
            width=60,
            fg_color=COLOR_ORANGE,
            command=self.start_request_thread,
        )
        self.send_btn.pack(side="left", padx=5)

        # 保存按钮
        ctk.CTkButton(
            top_frame,
            text="Save",
            text_color=TEXT_WHITE,
            width=40,
            fg_color=COLOR_BLUE,
            command=self.save_current_to_collection,
        ).pack(side="left", padx=2)

        # 导入/导出按钮
        ctk.CTkButton(
            top_frame,
            text="Import",
            text_color=TEXT_BLACK,
            width=40,
            fg_color=COLOR_GRAY,
            command=self.open_curl_import,
        ).pack(side="left", padx=(2, 1))

        ctk.CTkButton(
            top_frame,
            text="Export",
            text_color=TEXT_BLACK,
            width=40,
            fg_color=COLOR_GRAY,
            command=self.copy_as_curl,
        ).pack(side="left", padx=(1, 5))

    # =========================================
    # 请求参数区逻辑 (Request Tabs)
    # =========================================
    def setup_request_tabs(self):
        self.req_tabview = ctk.CTkTabview(
            self.main_area, height=300, text_color=TEXT_BLACK
        )
        self.req_tabview.pack(fill="x", pady=(0, 10))

        self.tab_params = self.req_tabview.add("Params")
        self.tab_headers = self.req_tabview.add("Headers")
        self.tab_auth = self.req_tabview.add("Auth")
        self.tab_body = self.req_tabview.add("Body")

        # 使用封装好的 KeyValueTable
        self.params_table = KeyValueTable(self.tab_params)
        self.params_table.pack(fill="both", expand=True)

        self.headers_table = KeyValueTable(
            self.tab_headers,
            suggestions=["Content-Type", "Authorization", "User-Agent", "Accept"],
        )
        self.headers_table.pack(fill="both", expand=True)

        # Auth Tab
        self.setup_auth_tab()

        # Body Tab
        body_ctrl = ctk.CTkFrame(self.tab_body, height=30, fg_color="transparent")
        body_ctrl.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(body_ctrl, text="JSON/Raw Body").pack(side="left")
        ctk.CTkButton(
            body_ctrl,
            text="Format JSON",
            width=80,
            height=24,
            fg_color=COLOR_BLUE,
            command=self.format_body_json,
        ).pack(side="right")

        self.text_body = ctk.CTkTextbox(self.tab_body, font=("Consolas", 12), undo=True)
        self.text_body.pack(fill="both", expand=True)

    def setup_auth_tab(self):
        ctrl = ctk.CTkFrame(self.tab_auth, fg_color="transparent")
        ctrl.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(ctrl, text="Type:").pack(side="left", padx=5)
        self.auth_type_var = ctk.StringVar(value="No Auth")
        ctk.CTkComboBox(
            ctrl,
            values=["No Auth", "Bearer Token", "Basic Auth"],
            variable=self.auth_type_var,
            command=self.update_auth_ui,
        ).pack(side="left", padx=5)

        self.auth_input_frame = ctk.CTkFrame(self.tab_auth, fg_color="transparent")
        self.auth_input_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.auth_widgets = {}
        self.update_auth_ui("No Auth")

    def update_auth_ui(self, choice):
        for w in self.auth_input_frame.winfo_children():
            w.destroy()

        self.auth_widgets = {}  # 重置
        if choice == "Bearer Token":
            entry = ctk.CTkEntry(self.auth_input_frame, placeholder_text="Token")
            entry.pack(fill="x", pady=5)
            self.auth_widgets["token"] = entry
        elif choice == "Basic Auth":
            u_entry = ctk.CTkEntry(self.auth_input_frame, placeholder_text="Username")
            u_entry.pack(fill="x", pady=5)
            p_entry = ctk.CTkEntry(
                self.auth_input_frame, placeholder_text="Password", show="*"
            )
            p_entry.pack(fill="x", pady=5)
            self.auth_widgets["username"] = u_entry
            self.auth_widgets["password"] = p_entry

    # =========================================
    # 响应显示区逻辑 (Response Area)
    # =========================================
    def setup_response_area(self):
        self.resp_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.resp_frame.pack(fill="both", expand=True)

        # Toolbar
        tool_bar = ctk.CTkFrame(self.resp_frame, height=40)
        tool_bar.pack(fill="x", pady=(0, 5))

        self.status_label = ctk.CTkLabel(
            tool_bar, text="Ready", font=("Arial", 12, "bold")
        )
        self.status_label.pack(side="left", padx=10)

        # Copy Button
        ctk.CTkButton(
            tool_bar,
            text="📋 Copy",
            text_color=TEXT_BLACK,
            width=60,
            height=24,
            fg_color=COLOR_GRAY,
            command=self.copy_response_text,
        ).pack(side="right", padx=5)

        # Search
        ctk.CTkButton(
            tool_bar, text="▼", width=24, command=lambda: self.navigate_search("next")
        ).pack(side="right", padx=1)
        ctk.CTkButton(
            tool_bar, text="▲", width=24, command=lambda: self.navigate_search("prev")
        ).pack(side="right", padx=1)

        self.search_entry = ctk.CTkEntry(
            tool_bar, placeholder_text="Find...", width=150
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.navigate_search("next"))

        # Text Content
        self.text_resp = ctk.CTkTextbox(self.resp_frame, font=("Consolas", 12))
        self.text_resp.pack(fill="both", expand=True)
        self.text_resp.configure(state="disabled")

        # 搜索高亮配置
        self.text_resp._textbox.tag_config(
            "search_highlight", background="#FFD700", foreground="black"
        )
        self.text_resp._textbox.tag_config(
            "current_match", background="#FF8C00", foreground="white"
        )

    # =========================================
    # 核心业务逻辑 (Request Execution)
    # =========================================
    def start_request_thread(self):
        self.send_btn.configure(state="disabled", text="...")
        self.status_label.configure(text="Sending...", text_color="orange")

        self.text_resp.configure(state="normal")
        self.text_resp.delete("0.0", "end")
        self.text_resp.configure(state="disabled")

        threading.Thread(target=self.run_request, daemon=True).start()

    def run_request(self):
        try:
            # 1. 收集 UI 数据
            method = self.method_var.get()
            url = self.url_entry.get().strip()
            params = self.params_table.get_data(as_dict=False)
            headers = self.headers_table.get_data(as_dict=True)
            body_raw = self.text_body.get("0.0", "end").strip()
            auth_type = self.auth_type_var.get()

            auth_data = {}
            if auth_type == "Bearer Token":
                auth_data["token"] = self.auth_widgets["token"].get()
            elif auth_type == "Basic Auth":
                auth_data["username"] = self.auth_widgets["username"].get()
                auth_data["password"] = self.auth_widgets["password"].get()

            # 2. 调用 Network 模块发送请求
            resp = send_http_request(
                method, url, params, headers, body_raw, auth_type, auth_data
            )

            # 3. 回调更新 UI (主线程)
            self.after(0, lambda: self.update_ui_success(resp))

            # 4. 记录日志 (UI + File)
            log_item = {
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "body": body_raw,
                "auth_type": auth_type,
                "status": resp.status_code,
            }
            # 更新内存
            self.logs.insert(0, log_item)
            if len(self.logs) > 30:
                self.logs.pop()

            # 写入文件 (调用 Storage 模块)
            append_log_to_file(method, url, resp.status_code)

            # 刷新历史记录侧边栏
            self.after(0, self.refresh_history_ui)

        except Exception as e:
            self.after(0, lambda: self.update_ui_error(str(e)))
            # 记录错误日志
            try:
                # 简单记录下错误，防止 run_request 崩溃
                append_log_to_file(self.method_var.get(), self.url_entry.get(), "ERROR")
            except:
                pass

    def update_ui_success(self, resp):
        self.send_btn.configure(state="normal", text="🚀")

        color = COLOR_GREEN if 200 <= resp.status_code < 300 else COLOR_RED
        size_kb = len(resp.content) / 1024
        self.status_label.configure(
            text=f"{resp.status_code} | {resp.elapsed.total_seconds():.2f}s | {size_kb:.1f}KB",
            text_color=color,
        )

        c_type = resp.headers.get("Content-Type", "").lower()

        # 图片处理逻辑 (调用弹窗模块)
        if "image" in c_type:
            content_text = f"[Image Content Detected]\nSize: {len(resp.content)} bytes\n\nImage has been opened in a new window."
            self.text_resp.configure(state="normal")
            self.text_resp.insert("0.0", content_text)
            self.text_resp.configure(state="disabled")

            ImagePopup.show(self, resp.content)
        else:
            # 文本处理逻辑
            try:
                content_text = json.dumps(resp.json(), indent=4, ensure_ascii=False)
            except:
                content_text = resp.text

            self.text_resp.configure(state="normal")
            self.text_resp.delete("0.0", "end")
            self.text_resp.insert("0.0", content_text)
            self.text_resp.configure(state="disabled")

    def update_ui_error(self, msg):
        self.send_btn.configure(state="normal", text="🚀")
        self.status_label.configure(text="Error", text_color=COLOR_RED)
        self.text_resp.configure(state="normal")
        self.text_resp.delete("0.0", "end")
        self.text_resp.insert("0.0", msg)
        self.text_resp.configure(state="disabled")

    # =========================================
    # 数据管理与工具函数
    # =========================================
    def save_current_to_collection(self):
        dialog = ctk.CTkInputDialog(text="Name:", title="Save Request")
        name = dialog.get_input()
        if name:
            item = {
                "name": name,
                "method": self.method_var.get(),
                "url": self.url_entry.get(),
                "headers": self.headers_table.get_data(),
                "params": self.params_table.get_data(False),
                "body": self.text_body.get("0.0", "end").strip(),
                "auth_type": self.auth_type_var.get(),
            }
            self.collections.append(item)
            save_collections(self.collections)
            self.refresh_collections_ui()

    def delete_collection_item_by_index(self, index):
        if 0 <= index < len(self.collections):
            del self.collections[index]
            save_collections(self.collections)
            self.refresh_collections_ui()

    def load_collection_item(self, index):
        self.restore_request_data(self.collections[index])
        if not self.sidebar_visible:
            self.toggle_sidebar()

    def load_history_item(self, index):
        self.restore_request_data(self.logs[index])
        if not self.sidebar_visible:
            self.toggle_sidebar()

    def clear_history(self):
        self.logs = []
        self.refresh_history_ui()

    def restore_request_data(self, data):
        """通用回填逻辑"""
        self.method_var.set(data.get("method", "GET"))
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, data.get("url", ""))

        self.params_table.set_data(data.get("params", []))
        self.headers_table.set_data(data.get("headers", {}))

        self.text_body.delete("0.0", "end")
        self.text_body.insert("0.0", data.get("body", ""))

        at = data.get("auth_type", "No Auth")
        self.auth_type_var.set(at)
        self.update_auth_ui(at)

    def format_body_json(self):
        try:
            content = self.text_body.get("0.0", "end").strip()
            formatted = json.dumps(json.loads(content), indent=4, ensure_ascii=False)
            self.text_body.delete("0.0", "end")
            self.text_body.insert("0.0", formatted)
        except:
            pass

    def copy_response_text(self):
        try:
            text = self.text_resp.get("0.0", "end").strip()
            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
                self.status_label.configure(text="Copied!", text_color="#3B8ED0")
                self.after(2000, lambda: self.status_label.configure(text_color="gray"))
        except:
            pass

    def navigate_search(self, direction):
        pattern = self.search_entry.get()
        if not pattern:
            return

        text_widget = self.text_resp._textbox
        # 清除旧高亮
        text_widget.tag_remove("search_highlight", "1.0", "end")
        text_widget.tag_remove("current_match", "1.0", "end")
        self.search_matches = []

        # 查找所有匹配
        start_pos = "1.0"
        while True:
            pos = text_widget.search(pattern, start_pos, stopindex="end", nocase=True)
            if not pos:
                break
            end_pos = text_widget.index(f"{pos} + {len(pattern)}c")
            self.search_matches.append((pos, end_pos))
            text_widget.tag_add("search_highlight", pos, end_pos)
            start_pos = end_pos

        if not self.search_matches:
            return

        # 移动索引
        if direction == "next":
            self.current_match_index = (self.current_match_index + 1) % len(
                self.search_matches
            )
        else:
            self.current_match_index = (
                self.current_match_index - 1 + len(self.search_matches)
            ) % len(self.search_matches)

        # 高亮当前匹配并滚动
        cur_start, cur_end = self.search_matches[self.current_match_index]
        text_widget.tag_add("current_match", cur_start, cur_end)
        text_widget.see(cur_start)

    def copy_as_curl(self):
        cmd = generate_curl_command(
            self.method_var.get(),
            self.url_entry.get().strip(),
            self.params_table.get_data(False),
            self.headers_table.get_data(True),
            self.text_body.get("0.0", "end").strip(),
        )
        self.clipboard_clear()
        self.clipboard_append(cmd)
        messagebox.showinfo("Copied", "cURL command copied to clipboard!")

    def open_curl_import(self):
        def on_import_success(data):
            self.restore_request_data(data)

        # 调用 Popups 模块
        CurlImportDialog(self, on_import_success)

    def setup_shortcuts(self):
        self.bind("<Control-Return>", lambda e: self.start_request_thread())
        self.bind("<Control-s>", lambda e: self.save_current_to_collection())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
