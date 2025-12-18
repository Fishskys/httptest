# Modern API Tester Ultimate

一个基于 Python 构建的现代化、轻量级 API 测试桌面工具。本项目旨在提供类似 Postman 的核心功能，同时保持极速启动和简洁的用户交互体验。

## 🌟 主要功能

* **全功能请求构建器**：支持 GET、POST、PUT、DELETE 等常用 HTTP 方法。
* **灵活的参数管理**：
  * **Params & Headers**：提供动态键值对表格，支持自动补全常用 Header 字段（如 Content-Type, Authorization）。
  * **Body 支持**：支持 Raw 文本和 JSON 输入，内置 JSON 格式化（Beautify）功能。


* **多重认证支持**：内置 No Auth、Bearer Token 以及 Basic Auth 认证模式，并提供动态切换的 UI 输入界面。
* **强大的响应展示**：
  * **智能预览**：自动识别响应类型。文本内容支持 JSON 高亮查找，图片内容则自动弹出独立窗口查看。
  * **文本搜索**：响应结果支持全文搜索，并提供高亮显示和快速导航。
* **效率工具**：
  * **cURL 互通**：支持从 cURL 命令直接导入请求，或将当前配置一键导出为标准 cURL 命令。
  * **收藏夹与历史记录**：侧边栏自动记录最近的请求历史，并支持将常用 API 永久保存至收藏夹。


* **异步并发处理**：基于多线程执行网络请求，确保在等待 API 响应时 UI 界面始终保持流畅，不卡顿。

## ✨ 核心特色

* **现代化的 UI 界面**：采用 `CustomTkinter` 库，支持系统级深色/浅色模式切换，界面风格精致且符合现代审美。
* **模块化架构**：项目经过精心重构，采用 MVC 模式设计，将 UI 组件、网络逻辑、数据持久化完全解耦，易于二次开发和维护。
* **轻量且绿色**：无须安装庞大的运行时环境，支持打包为独立的可执行文件（EXE），运行资源占用极低。
* **本地化数据存储**：历史记录和收藏夹数据均加密存储于本地 JSON 文件中，不经过任何第三方服务器，保护 API 调试隐私。

## 🛠️ 技术栈

* **GUI 框架**：`CustomTkinter` & `Tkinter`
* **网络引擎**：`Requests`
* **解析工具**：`Uncurl` (cURL 解析), `Pillow` (图像处理)
* **并发模型**：`Threading`

## 🚀 快速开始

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **运行程序**：
```bash
python main.py
```

3.打包成exe(可选)
```bash
pip install nuitka
nuitka --onefile --enable-plugin=tk-inter --windows-console-mode=disable --include-package=customtkinter --output-dir=dist main.py
```

---

## 更新历史

2025.12.15更新：增加log

2025.12.16更新：增加收藏、导入、导出功能，重构了项目结构，优化了ui

2025.12.18更新，使用nuitka打包