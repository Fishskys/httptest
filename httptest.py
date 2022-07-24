from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
import requests
import json
from PIL import Image
from io import BytesIO


class HttpTest:

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('httptest.ui')
        self.ui.send_button.clicked.connect(self.send)
        self.ui.add_button.clicked.connect(self.addline)
        self.ui.minus_button.clicked.connect(self.minusline)
        self.ui.pic_button.clicked.connect(self.showpic)

    def send(self):
        # 获取请求方法
        method = self.ui.comboBox.currentText()
        # 获取url
        url = self.ui.lineEdit.text()
        if url == '':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入url！')
            return
        headers = {}
        # 获取消息头
        row_count = self.ui.table.rowCount()
        for i in range(row_count):
            if self.ui.table.item(i, 0) and self.ui.table.item(i, 1):
                headers[self.ui.table.item(i, 0).text()] = self.ui.table.item(i, 1).text()
        # print(headers)

        # 获取消息体
        str_data = self.ui.data_textEdit.toPlainText()
        # 解码，注：解码之后为字典
        key = self.ui.key_name.text()  # url关键字
        data = {}
        if bool(str_data):
            data = json.loads(str_data)
        try:
            if method == 'GET':
                response = requests.get(url=url, headers=headers)
                # 提取url链接并自动填写，需要手动指定key
                res_dict = json.loads(response.text)
                if key in res_dict:
                    self.ui.pic_edit.setText(res_dict[key])

                self.ui.output_textedit.setPlainText(response.text)
            elif method == 'POST':
                response = requests.post(url=url, headers=headers, data=data)

                res_dict = json.loads(response.text)
                if key in res_dict:
                    self.ui.pic_edit.setText(res_dict[key])

                self.ui.output_textedit.setPlainText(response.text)
        except requests.exceptions.MissingSchema:
            QMessageBox.critical(
                self.ui,
                '错误',
                '错误的url！')
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self.ui,
                '错误',
                '无效的url！')

    # 消息头增删操作
    def addline(self):
        row_count = self.ui.table.rowCount()
        self.ui.table.setRowCount(row_count + 1)

    def minusline(self):
        row_count = self.ui.table.rowCount()
        self.ui.table.setRowCount(row_count - 1)

    def showpic(self):
        url = self.ui.pic_edit.text()
        if url == '':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入图片url！')
            return

        try:
            response = requests.get(url=url)
            i = Image.open(BytesIO(response.content))
            i.show()
        except requests.exceptions.MissingSchema:
            QMessageBox.critical(
                self.ui,
                '错误',
                '错误的url！')
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self.ui,
                '错误',
                '无效的url！')


if __name__ == "__main__":
    print("请不要关闭此窗口")
    app = QApplication([])
    HttpTest = HttpTest()
    HttpTest.ui.show()
    app.exec_()
    input("按任意键退出")
