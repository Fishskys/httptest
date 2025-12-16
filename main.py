from src.config import init_app_settings
from src.ui.main_window import APITesterApp

if __name__ == "__main__":
    init_app_settings()
    app = APITesterApp()
    app.mainloop()
