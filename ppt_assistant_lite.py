import os
import sys
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import *
import easyocr
import pyautogui
from openai import OpenAI

class AISettingsDialog(QDialog):
    def __init__(self, parent=None, current_prompt=""):
        super().__init__(parent)
        self.setWindowTitle("AI角色设定")
        layout = QVBoxLayout(self)
        self.prompt_edit = QTextEdit(current_prompt)
        layout.addWidget(self.prompt_edit)
        layout.addWidget(QPushButton("确认", clicked=self.accept))

    def get_prompt(self):
        return self.prompt_edit.toPlainText()

class PPTAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.init_window()
        self.init_services()
        self.init_ui()
        self.show()

    def init_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(390, 374)
        self.resize(450, 463)

    def init_services(self):
        self.resource_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        self.reader = None
        self.ai_prompt = "你就是苏轼，直接用苏轼的口吻对话，语言简洁，现在是你在黄州作词定风波的时期"
        self.ai_client = OpenAI(api_key="sk-11f1178aba3548369a489252be37829b", base_url="https://api.deepseek.com")

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # 左侧布局
        left = QVBoxLayout()
        self.character_image = QLabel()
        character_path = os.path.join(self.resource_dir, "character.png")
        if not os.path.exists(character_path):
            character_path = "C:/Users/Tsang/Pictures/character.png"
        self.character_image.setPixmap(QPixmap(character_path).scaled(150, 150, Qt.KeepAspectRatio))
        left.addWidget(self.character_image)
        left.addStretch()
        
        # 右侧布局
        right = QVBoxLayout()
        
        # 按钮区域
        buttons = QHBoxLayout()
        for text, slot in [("截图识别", self.process_screen), ("AI设置", self.open_ai_settings), ("关闭", self.close)]:
            btn = QPushButton(text, clicked=slot)
            btn.setStyleSheet("padding: 8px;")
            buttons.addWidget(btn)
        right.addLayout(buttons)
        
        # 对话气泡
        self.response_bubble = QLabel()
        self.response_bubble.setStyleSheet(
            "color: black; background-color: white; padding: 10px; "
            "border-radius: 10px; border: 1px solid #ddd; "
            "min-width: 200px; max-width: 250px;"
        )
        self.response_bubble.setWordWrap(True)
        right.addWidget(self.response_bubble)
        
        # 输入区域
        self.user_input = QTextEdit(placeholderText="在这里输入您的问题...", maximumHeight=80)
        right.addWidget(self.user_input)
        right.addWidget(QPushButton("发送", clicked=self.handle_user_input))
        
        layout.addLayout(left)
        layout.addLayout(right)

    def process_screen(self):
        try:
            if self.reader is None:
                self.reader = easyocr.Reader(['ch_sim'], gpu=False)
            
            self.hide()
            screenshot = pyautogui.screenshot()
            self.show()
            
            temp_file = os.path.join(os.environ['TEMP'], 'screenshot.png')
            screenshot.save(temp_file)
            
            results = self.reader.readtext(temp_file, batch_size=1, detail=0)
            text = ' '.join(results) if results else "未识别到文本"
            
            if text != "未识别到文本":
                self.get_ai_response(text)
            
            os.remove(temp_file)
            
        except Exception as e:
            self.response_bubble.setText(f"错误: {str(e)}")

    def get_ai_response(self, text):
        try:
            self.response_bubble.setText("思考中...")
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.ai_prompt},
                    {"role": "user", "content": text},
                ],
                max_tokens=500,
                stream=True
            )
            
            reply = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    reply += chunk.choices[0].delta.content
                    self.response_bubble.setText(reply)
                    QApplication.processEvents()
            
        except Exception as e:
            self.response_bubble.setText(f"AI响应错误: {str(e)}")

    def handle_user_input(self):
        text = self.user_input.toPlainText().strip()
        if text:
            self.get_ai_response(text)
            self.user_input.clear()

    def open_ai_settings(self):
        dialog = AISettingsDialog(self, self.ai_prompt)
        if dialog.exec_():
            self.ai_prompt = dialog.get_prompt()
            self.response_bubble.setText("AI角色设定已更新")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    assistant = PPTAssistant()
    sys.exit(app.exec_())