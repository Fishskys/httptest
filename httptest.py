import customtkinter as ctk
import requests
import json
import threading
import yaml
import os
import datetime
from tkinter import messagebox

# 全局设置
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class KeyValueTable(ctk.CTkFrame):
    """
    自定义控件：键值对表格
    """

    def __init__(self, master, title="Params", suggestions=None):
        super().__init__(master)
        self.rows = []
        self.suggestions = suggestions

        # 1. 顶部控制栏
        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", padx=5, pady=5)

        self.label = ctk.CTkLabel(
            self.ctrl_frame, text=title, font=("Arial", 14, "bold")
        )
        self.label.pack(side="left", padx=5)

        self.btn_remove = ctk.CTkButton(
            self.ctrl_frame,
            text="-",
            width=30,
            height=24,
            fg_color="#FF4B4B",
            hover_color="#D32F2F",
            command=self.remove_last_row,
        )
        self.btn_remove.pack(side="right", padx=2)

        self.btn_add = ctk.CTkButton(
            self.ctrl_frame, text="+", width=30, height=24, command=self.add_row
        )
        self.btn_add.pack(side="right", padx=2)

        # 2. 表头
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(5, 0))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=2)

        ctk.CTkLabel(self.header_frame, text="Key", text_color="gray", anchor="w").grid(
            row=0, column=0, sticky="ew"
        )
        ctk.CTkLabel(
            self.header_frame, text="Value", text_color="gray", anchor="w"
        ).grid(row=0, column=1, sticky="ew", padx=5)

        # 3. 可滚动区域
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, height=150, fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.add_row()

    def add_row(self):
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=2)

        if self.suggestions:
            k_entry = ctk.CTkComboBox(row_frame, values=self.suggestions, height=28)
        else:
            k_entry = ctk.CTkEntry(row_frame, placeholder_text="Key", height=28)

        k_entry.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        v_entry = ctk.CTkEntry(row_frame, placeholder_text="Value", height=28)
        v_entry.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        self.rows.append({"frame": row_frame, "key": k_entry, "value": v_entry})

    def remove_last_row(self):
        if self.rows:
            last_row = self.rows.pop()
            last_row["frame"].destroy()

    def get_data(self):
        data = {}
        for row in self.rows:
            k = row["key"].get().strip()
            v = row["value"].get().strip()
            if k:
                data[k] = v
        return data


class APITesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern API Tester Pro")
        self.geometry("1000x750")

        self.logs = []
        self.header_presets = self.load_header_presets()

        self.main_tabs = ctk.CTkTabview(self)
        self.main_tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_tester = self.main_tabs.add("API Tester")
        self.tab_logs = self.main_tabs.add("Logs (Last 20)")

        self.setup_tester_tab()
        self.setup_logs_tab()

    def load_header_presets(self):
        filename = "headers.yaml"
        defaults = [
            "Content-Type",
            "Authorization",
            "User-Agent",
            "Accept",
            "Cache-Control",
        ]

        if not os.path.exists(filename):
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    yaml.dump(defaults, f)
            except:
                pass
            return defaults

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, list) else defaults
        except:
            return defaults

    def setup_tester_tab(self):
        container = self.tab_tester
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)

        # --- Top: URL ---
        top_frame = ctk.CTkFrame(container)
        top_frame.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        self.method_var = ctk.StringVar(value="GET")
        self.method_combo = ctk.CTkComboBox(
            top_frame,
            values=["GET", "POST", "PUT", "DELETE", "PATCH"],
            variable=self.method_var,
            width=80,
        )
        self.method_combo.grid(row=0, column=0, padx=10, pady=10)

        self.url_entry = ctk.CTkEntry(top_frame, placeholder_text="Enter request URL")
        self.url_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.send_btn = ctk.CTkButton(
            top_frame, text="发送", command=self.start_request_thread, width=100
        )
        self.send_btn.grid(row=0, column=2, padx=10, pady=10)

        # --- Middle: Params & Headers ---
        middle_frame = ctk.CTkFrame(container, fg_color="transparent")
        middle_frame.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=1)
        middle_frame.grid_rowconfigure(0, weight=1)

        self.params_table = KeyValueTable(middle_frame, title="Params")
        self.params_table.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        self.headers_table = KeyValueTable(
            middle_frame, title="Headers", suggestions=self.header_presets
        )
        self.headers_table.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        # --- Bottom: Body & Response ---
        bottom_frame = ctk.CTkFrame(container, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=1)

        # Body
        body_ctrl = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=30)
        body_ctrl.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(body_ctrl, text="Body (JSON)", font=("Arial", 12, "bold")).pack(
            side="left"
        )
        ctk.CTkButton(
            body_ctrl,
            text="清空",
            width=50,
            height=20,
            fg_color="gray",
            command=lambda: self.text_body.delete("0.0", "end"),
        ).pack(side="right")
        self.text_body = ctk.CTkTextbox(bottom_frame, font=("Consolas", 12))
        self.text_body.grid(row=1, column=0, padx=(0, 5), sticky="nsew")

        # Response
        resp_ctrl = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=30)
        resp_ctrl.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.status_label = ctk.CTkLabel(
            resp_ctrl, text="Response: Ready", font=("Arial", 12, "bold")
        )
        self.status_label.pack(side="left")

        self.text_resp = ctk.CTkTextbox(bottom_frame, font=("Consolas", 12))
        self.text_resp.grid(row=1, column=1, padx=(5, 0), sticky="nsew")
        self.text_resp.configure(state="disabled")

    def setup_logs_tab(self):
        """构建日志界面"""
        container = self.tab_logs
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # 使用一个只读的 Textbox 来显示日志
        self.log_textbox = ctk.CTkTextbox(container, font=("Consolas", 12))
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.log_textbox.insert("0.0", "暂无请求记录...\n")
        self.log_textbox.configure(state="disabled")

        # 已移除手动刷新按钮

    def start_request_thread(self):
        self.send_btn.configure(state="disabled", text="...")
        self.status_label.configure(text="Sending...", text_color="orange")
        threading.Thread(target=self.run_request).start()

    def run_request(self):
        method = self.method_var.get()
        url = self.url_entry.get().strip()
        params = self.params_table.get_data()
        headers = self.headers_table.get_data()

        body_raw = self.text_body.get("0.0", "end").strip()
        json_data = None
        if body_raw and method in ["POST", "PUT", "PATCH"]:
            try:
                json_data = json.loads(body_raw)
            except Exception as e:
                self.update_ui_error(f"JSON Error: {e}")
                return

        if not url:
            self.update_ui_error("URL Empty")
            return

        try:
            start_time = datetime.datetime.now()
            resp = requests.request(
                method, url, params=params, headers=headers, json=json_data, timeout=10
            )

            # 记录日志
            self.add_log(
                method, url, params, json_data, resp.status_code, resp.text, start_time
            )

            self.update_ui_success(resp)
        except Exception as e:
            self.add_log(
                method, url, params, json_data, "ERROR", str(e), datetime.datetime.now()
            )
            self.update_ui_error(str(e))

    def add_log(self, method, url, params, body, status, result, start_time):
        """添加一条日志到内存并保存到文件"""

        # 1. 保存到本地文件 (追加模式)
        try:
            log_dir = "log"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            date_str = start_time.strftime("%Y-%m-%d")
            file_path = os.path.join(log_dir, f"{date_str}.log")

            # 构造完整的日志内容
            file_content = (
                f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] {method} {url}\n"
                f"Status: {status}\n"
                f"Params: {params}\n"
                f"Body: {body}\n"
                f"Response: {result}\n"
                f"{'-'*60}\n"
            )

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(file_content)
        except Exception as e:
            print(f"日志文件写入错误: {e}")

        # 2. 更新内存数据 (用于界面显示，只保留最近20条)
        log_entry = {
            "time": start_time.strftime("%H:%M:%S"),
            "method": method,
            "url": url,
            "params": params,
            "body": body,
            "status": status,
            "result_preview": (
                result[:200] + "..." if len(str(result)) > 200 else str(result)
            ),
        }

        self.logs.insert(0, log_entry)
        if len(self.logs) > 20:
            self.logs.pop()

        # 3. 自动刷新界面
        self.after(10, self.render_logs)

    def render_logs(self):
        """将内存中的日志渲染到文本框"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("0.0", "end")

        if not self.logs:
            self.log_textbox.insert("0.0", "暂无请求记录...")
        else:
            for log in self.logs:
                log_str = (
                    f"[{log['time']}] {log['method']} {log['url']}\n"
                    f"Status: {log['status']}\n"
                    f"Params: {log['params']}\n"
                    f"Body: {log['body']}\n"
                    f"Response: {log['result_preview']}\n"
                    f"{'-'*60}\n"
                )
                self.log_textbox.insert("end", log_str)

        self.log_textbox.configure(state="disabled")

    def update_ui_success(self, resp):
        self.send_btn.configure(state="normal", text="发送")
        color = "#2CC985" if 200 <= resp.status_code < 300 else "#FF4B4B"
        self.status_label.configure(
            text=f"Status: {resp.status_code} | {resp.elapsed.total_seconds():.2f}s",
            text_color=color,
        )

        try:
            content = json.dumps(resp.json(), indent=4, ensure_ascii=False)
        except:
            content = resp.text

        self.text_resp.configure(state="normal")
        self.text_resp.delete("0.0", "end")
        self.text_resp.insert("0.0", content)
        self.text_resp.configure(state="disabled")

    def update_ui_error(self, msg):
        self.send_btn.configure(state="normal", text="发送")
        self.status_label.configure(text="Error", text_color="#FF4B4B")
        self.text_resp.configure(state="normal")
        self.text_resp.delete("0.0", "end")
        self.text_resp.insert("0.0", msg)
        self.text_resp.configure(state="disabled")


if __name__ == "__main__":
    app = APITesterApp()
    app.mainloop()
