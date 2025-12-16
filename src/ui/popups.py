import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import io
from src.core.converters import parse_curl_command


class ImagePopup:
    @staticmethod
    def show(master, image_bytes):
        try:
            top = ctk.CTkToplevel(master)
            top.title("Image Preview")
            top.geometry("600x500")
            top.attributes("-topmost", True)

            pil_image = Image.open(io.BytesIO(image_bytes))

            # 缩放逻辑
            max_w, max_h = 800, 600
            w, h = pil_image.size
            ratio = min(max_w / w, max_h / h, 1.0)
            new_size = (int(w * ratio), int(h * ratio))

            ctk_img = ctk.CTkImage(
                light_image=pil_image, dark_image=pil_image, size=new_size
            )

            ctk.CTkLabel(top, text="", image=ctk_img).pack(
                expand=True, fill="both", padx=20, pady=20
            )
            ctk.CTkLabel(
                top,
                text=f"Original Size: {w}x{h} | Format: {pil_image.format}",
                text_color="gray",
            ).pack(side="bottom", pady=5)
        except Exception as e:
            messagebox.showerror("Image Error", str(e))


class CurlImportDialog:
    def __init__(self, master, callback):
        self.top = ctk.CTkToplevel(master)
        self.top.title("Import cURL")
        self.top.geometry("600x400")
        self.callback = callback

        self.txt = ctk.CTkTextbox(self.top)
        self.txt.pack(fill="both", expand=True)

        ctk.CTkButton(self.top, text="Import", command=self.run).pack(pady=5)

    def run(self):
        cmd = self.txt.get("0.0", "end").strip()
        try:
            data = parse_curl_command(cmd)
            self.callback(data)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Parse Error", str(e))
