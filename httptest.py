from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem
from PyQt5 import uic
import requests
import json
from PIL import Image
from io import BytesIO
import pyperclip
import yaml


class HttpTest:

    def __init__(self):
        conf_yaml = open("conf.yaml", "r", encoding="utf-8")
        conf = yaml.load(conf_yaml, Loader=yaml.FullLoader)
        self.pre_headers = conf["headers"]
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = uic.loadUi("httptest.ui")
        self.ui.setWindowTitle("httptest")

        self.ui.send_button.clicked.connect(self.send)
        self.ui.picshow_button.clicked.connect(self.show_pic)
        # 参数params
        self.ui.param_add_button.clicked.connect(self.add_param)
        self.ui.param_minus_button.clicked.connect(self.minus_param)

        # 消息头Headers
        self.ui.header_add_button.clicked.connect(self.add_header)
        self.ui.header_minus_button.clicked.connect(self.minus_header)

        # 请求体data
        self.ui.data_clearbutton.clicked.connect(self.clear_data)

        # output
        self.ui.copybutton.clicked.connect(self.copy_output)
        self.ui.output_clearbutton.clicked.connect(self.clear_output)

    def send(self):
        # 获取请求方法和url
        method = self.ui.method_comboBox.currentText()
        url = self.ui.url_lineEdit.text()
        if url == "":
            QMessageBox.critical(self.ui, "错误", "请输入url！")
            return

        # 获取请求参数
        params = {}
        row_count = self.ui.param_table.rowCount()
        if row_count > 0:
            for i in range(row_count):
                if self.ui.param_table.item(i, 0) and self.ui.param_table.item(i, 1):
                    params[self.ui.param_table.item(i, 0).text()] = (
                        self.ui.param_table.item(i, 1).text()
                    )

        # 获取消息头
        headers = {}
        row_count = self.ui.header_table.rowCount()
        if row_count > 0:
            for i in range(row_count):
                if self.ui.header_table.item(i, 0) and self.ui.header_table.item(i, 1):
                    headers[self.ui.header_table.item(i, 0).text()] = (
                        self.ui.header_table.item(i, 1).text()
                    )

        # 获取消息体
        str_data = self.ui.data_textEdit.toPlainText()
        # 解码，注：解码之后为字典
        key = self.ui.key_name.text()  # url关键字
        data = {}
        if bool(str_data):
            data = json.loads(str_data)
        try:
            if method == "GET":
                response = requests.get(url=url, params=params, headers=headers)
                if key:
                    # 提取url链接并自动填写，需要手动指定key
                    res_dict = json.loads(response.text)
                    # 判断返回字符串是字典还是列表包着的字典
                    if type(res_dict) == dict:
                        if key in res_dict:
                            self.ui.pic_lineEdit.setText(res_dict[key])
                    if type(res_dict) == list:
                        for item in res_dict:
                            if key in item:
                                self.ui.pic_lineEdit.setText(item[key])
                self.ui.output_textEdit.setPlainText(response.text)

            elif method == "POST":
                response = requests.post(url=url, headers=headers, data=data)
                if key:
                    res_dict = json.loads(response.text)
                    if type(res_dict) == dict:
                        if key in res_dict:
                            self.ui.pic_lineEdit.setText(res_dict[key])
                    if type(res_dict) == list:
                        for item in res_dict:
                            if key in item:
                                self.ui.pic_lineEdit.setText(item[key])
                self.ui.output_textEdit.setPlainText(response.text)

            elif method == "PUT":
                response = requests.put(url=url, headers=headers, data=data)
                if key:
                    res_dict = json.loads(response.text)
                    if type(res_dict) == dict:
                        if key in res_dict:
                            self.ui.pic_lineEdit.setText(res_dict[key])
                    if type(res_dict) == list:
                        for item in res_dict:
                            if key in item:
                                self.ui.pic_lineEdit.setText(item[key])
                self.ui.output_textEdit.setPlainText(response.text)

        except requests.exceptions.MissingSchema:
            QMessageBox.critical(self.ui, "错误", "错误的url！")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self.ui, "错误", "无效的url！")

    # param增删操作
    def add_param(self):
        row_count = self.ui.param_table.rowCount()
        self.ui.param_table.setRowCount(row_count + 1)

    def minus_param(self):
        row_count = self.ui.param_table.rowCount()
        if row_count > 0:
            self.ui.param_table.setRowCount(row_count - 1)

    # 消息头增删操作
    def add_header(self):
        row_count = self.ui.header_table.rowCount()
        self.ui.header_table.setRowCount(row_count + 1)

        # 添加预设内容
        row_count = self.ui.header_table.rowCount()
        pre_header = self.ui.preheaders_comboBox.currentText()
        # 每一个单元格是一个QTableWidgetItem对象，未实例化之前用这个方法设置单元格内容
        if pre_header != "None":
            self.ui.header_table.setItem(row_count - 1, 0, QTableWidgetItem(pre_header))
            self.ui.header_table.setItem(
                row_count - 1, 1, QTableWidgetItem(self.pre_headers[pre_header])
            )

    def minus_header(self):
        row_count = self.ui.header_table.rowCount()
        self.ui.header_table.setRowCount(row_count - 1)

    # 图片显示键
    def show_pic(self):
        url = self.ui.pic_lineEdit.text()
        if url == "":
            QMessageBox.critical(self.ui, "错误", "请输入图片url！")
            return

        try:
            response = requests.get(url=url)
            i = Image.open(BytesIO(response.content))
            i.show()
        except requests.exceptions.MissingSchema:
            QMessageBox.critical(self.ui, "错误", "错误的url！")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self.ui, "错误", "无效的url！")

    # 复制返回内容
    def copy_output(self):
        text = self.ui.output_textEdit.toPlainText()
        pyperclip.copy(text)

    # 清除返回内容
    def clear_output(self):
        self.ui.output_textEdit.setPlainText("")

    # 清除请求体
    def clear_data(self):
        self.ui.data_textEdit.setPlainText("")


if __name__ == "__main__":
    print("请不要关闭此窗口")
    app = QApplication([])
    HttpTest = HttpTest()
    HttpTest.ui.show()
    app.exec_()
    # input("按任意键退出")
