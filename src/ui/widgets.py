import customtkinter as ctk
from src.config import COLOR_BLUE


class KeyValueTable(ctk.CTkFrame):
    def __init__(self, master, suggestions=None):
        super().__init__(master, fg_color="transparent")
        self.rows = []
        self.suggestions = suggestions

        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", padx=2, pady=(0, 5))

        # 按钮颜色使用 config 中的常量
        ctk.CTkButton(
            self.ctrl_frame,
            text="Clear",
            width=60,
            height=30,
            fg_color=COLOR_BLUE,
            command=self.clear,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            self.ctrl_frame,
            text="-",
            width=45,
            height=30,
            fg_color=COLOR_BLUE,
            command=self.remove_last_row,
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            self.ctrl_frame,
            text="+",
            width=45,
            height=30,
            fg_color=COLOR_BLUE,
            command=self.add_row,
        ).pack(side="right", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        self.add_row()

    # ... (add_row, remove_last_row, clear, set_data, get_data 的代码与原版一致，直接复制即可) ...

    def add_row(self, key_text="", value_text=""):
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=1)
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=2)

        if self.suggestions:
            k_entry = ctk.CTkComboBox(
                row_frame, values=self.suggestions, height=24, font=("Arial", 11)
            )
        else:
            k_entry = ctk.CTkEntry(
                row_frame, placeholder_text="Key", height=24, font=("Arial", 11)
            )

        if key_text:
            k_entry.set(str(key_text))
        k_entry.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        v_entry = ctk.CTkEntry(
            row_frame, placeholder_text="Value", height=24, font=("Arial", 11)
        )
        if value_text:
            v_entry.insert(0, str(value_text))
        v_entry.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        self.rows.append({"frame": row_frame, "key": k_entry, "value": v_entry})

    def remove_last_row(self):
        if self.rows:
            self.rows.pop()["frame"].destroy()

    def clear(self):
        for row in self.rows:
            row["frame"].destroy()
        self.rows = []
        self.add_row()

    def set_data(self, data):
        self.clear()
        # 清除默认添加的空行，因为clear会加一行
        self.rows[0]["frame"].destroy()
        self.rows = []

        if not data:
            self.add_row()
            return
        items = data.items() if isinstance(data, dict) else data
        for k, v in items:
            self.add_row(k, v)

    def get_data(self, as_dict=True):
        if as_dict:
            return {
                r["key"].get().strip(): r["value"].get().strip()
                for r in self.rows
                if r["key"].get().strip()
            }
        else:
            return [
                (r["key"].get().strip(), r["value"].get().strip())
                for r in self.rows
                if r["key"].get().strip()
            ]
