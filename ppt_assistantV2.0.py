import os
import sys
import time

import keyboard
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QTextEdit, QDialog, QHBoxLayout,
                             QScrollArea, QFrame)
from openai import OpenAI


class AISettingsDialog(QDialog):
    def __init__(self, parent=None, current_prompt=""):
        super().__init__(parent)
        self.setWindowTitle("AI角色设定")
        self.resize(400, 300)
        self.setStyleSheet("background: white;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        prompt_label = QLabel("请输入AI角色设定：")
        prompt_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(prompt_label)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setText(current_prompt)
        self.prompt_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                min-height: 180px;
            }
        """)
        layout.addWidget(self.prompt_edit)

        confirm_btn = QPushButton("保存设定")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

        self.setLayout(layout)

    def get_prompt(self):
        return self.prompt_edit.toPlainText()


class PPTAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.resource_dir = self.get_resource_path()
        self.print_debug_info()
        # 添加字体大小设置，默认为22px
        self.font_size = 22
        self.init_ui()
        self.setup_ai()
        self.show()

    def get_resource_path(self):
        """获取资源文件路径（兼容打包和开发环境）"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "resource")

    def print_debug_info(self):
        """打印调试信息"""
        print("=" * 50)
        print(f"Python版本: {sys.version}")
        print(f"资源目录: {self.resource_dir}")
        img_path = os.path.join(self.resource_dir, "character.png")
        print(f"图片路径: {img_path}")
        print(f"图片存在: {os.path.exists(img_path)}")
        print("=" * 50)

    def init_ui(self):
        self.setWindowTitle('东坡居士')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #文本框大小设置
        #
        #
        self.setMinimumSize(1000, 520)
        self.setStyleSheet("background: rgba(245, 245, 245, 0.95);")

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 顶部控制栏
        top_bar = QFrame()
        top_bar.setStyleSheet("background: transparent;")
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # 设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.9);
                padding: 8px 15px;
                border-radius: 15px;
                color: #333;
                border: 1px solid #ddd;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(245,245,245,0.9);
            }
        """)
        self.settings_btn.clicked.connect(self.open_ai_settings)

        # 添加字体大小设置按钮
        self.font_size_btn = QPushButton("Aa 字体")
        self.font_size_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.9);
                padding: 8px 15px;
                border-radius: 15px;
                color: #333;
                border: 1px solid #ddd;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(245,245,245,0.9);
            }
        """)
        self.font_size_btn.clicked.connect(self.change_font_size)

        # 关闭按钮
        self.close_btn = QPushButton("⨉ 关闭")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,100,100,0.9);
                padding: 8px 15px;
                border-radius: 15px;
                color: white;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,70,70,0.9);
            }
        """)
        self.close_btn.clicked.connect(self.close)

        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.font_size_btn)  # 添加字体大小按钮
        top_bar_layout.addWidget(self.settings_btn)
        top_bar_layout.addWidget(self.close_btn)
        top_bar.setLayout(top_bar_layout)

        # 内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # 左侧角色面板
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
        """)
        left_layout = QVBoxLayout()

        # 角色图片加载（兼容Python 3.8路径处理）
        character_img = QLabel()
        img_path = os.path.normpath(os.path.join(self.resource_dir, "character.png"))
        pixmap = QPixmap(img_path)

        if not pixmap.isNull():
            character_img.setPixmap(pixmap.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            error_msg = "图片加载失败:\n路径: {}\n请检查：\n1. 文件是否存在\n2. 文件格式是否正确\n3. 文件权限".format(
                img_path)
            character_img.setText(error_msg)
            character_img.setStyleSheet("color: #ff4444; font-size: 12px; line-height: 1.5;")

        character_img.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(character_img)

        # 角色简介
        desc_label = QLabel("东坡居士\n\n字子瞻，号东坡居士\n北宋文学家、书法家\n唐宋八大家之一")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin-top: 15px;
            line-height: 1.5;
        """)
        left_layout.addWidget(desc_label)
        left_panel.setLayout(left_layout)

        # 右侧对话面板
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
        """)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 对话历史
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: none;
                background: transparent;
                font-size: 18px;  # 加大字体
                color: #333;
                padding: 10px;
            }
        """)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.chat_history)
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

        # 输入区域
        input_layout = QHBoxLayout()
        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("输入您的问题...")
        self.user_input.setMaximumHeight(60)
        self.user_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background: white;
            }
        """)
        input_layout.addWidget(self.user_input)

        send_btn = QPushButton("发送")
        send_btn.setFixedSize(80, 50)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        send_btn.clicked.connect(self.handle_user_input)
        input_layout.addWidget(send_btn)
        right_layout.addLayout(input_layout)

        right_panel.setLayout(right_layout)

        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)

        main_layout.addWidget(top_bar)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # 设置热键（兼容Windows/Linux）
        keyboard.add_hotkey('ctrl+enter', self.focus_input)

    def focus_input(self):
        self.user_input.setFocus()

    def setup_ai(self):
        self.ai_prompt = """你此刻就是苏东坡本人，请遵循以下设定：
1. 使用宋代文人常用的表达方式
2. 适当引用东坡诗词
3. 保持豁达开朗的语气
4. 对现代事物保持合理认知局限
5. 回答控制在200字内"""

        self.ai_client = OpenAI(
            api_key="sk-11f1178aba3548369a489252be37829b",
            base_url="https://api.deepseek.com"
        )

    def handle_user_input(self):
        user_text = self.user_input.toPlainText().strip()
        if not user_text:
            return

        self.append_message("你", user_text)
        self.user_input.clear()

        try:
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.ai_prompt},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=500,
                stream=True
            )

            # 初始化消息块
            cursor = self.chat_history.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertHtml(
                f'<div style="color: #2c3e50; background: #ecf0f1; border-radius: 8px; padding: 10px 15px; margin: 8px 0; font-size: {self.font_size}px;">')
            cursor.insertHtml('<b>东坡居士:</b><br>')

            full_reply = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    part = chunk.choices[0].delta.content
                    full_reply += part

                    # 处理特殊字符（兼容Python 3.8）
                    processed_part = part.replace('\n', '<br>').replace('\\', '')
                    cursor.insertHtml(processed_part)
                    self.chat_history.ensureCursorVisible()
                    QApplication.processEvents()
                    time.sleep(0.03)

            # 闭合div标签
            cursor.insertHtml('</div>')
            self.chat_history.ensureCursorVisible()

        except Exception as e:
            error_msg = f"对话出错：{str(e)}".replace('\\', '/')  # 路径兼容处理
            self.append_message("系统", error_msg)

    def append_message(self, sender, text):
        """兼容Python 3.8的消息添加方法"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.End)

        # 预处理特殊字符
        processed_text = text.replace('\n', '<br>').replace('\\', '')

        # 使用类变量中的字体大小
        font_size = f"{self.font_size}px"

        # 输出格式调整
        message = f'<b>{sender}:</b><br>{processed_text}<br><br>'
        cursor.insertHtml(f'<div style="font-size: {font_size};">{message}</div>')
        self.chat_history.ensureCursorVisible()

    def open_ai_settings(self):
        dialog = AISettingsDialog(self, self.ai_prompt)
        if dialog.exec_():
            self.ai_prompt = dialog.get_prompt()
            self.append_message("系统", "角色设定已更新")

    # 将 change_font_size 方法移到这里，与 open_ai_settings 同级
    def change_font_size(self):
        """调整字体大小的方法"""
        # 循环切换字体大小：18px -> 22px -> 26px -> 18px
        if self.font_size == 18:
            self.font_size = 22
        elif self.font_size == 22:
            self.font_size = 26
        else:
            self.font_size = 18

        # 更新按钮文本以显示当前字体大小
        self.font_size_btn.setText(f"Aa 字体({self.font_size})")

        # 更新聊天历史的字体大小
        self.chat_history.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background: transparent;
                font-size: {self.font_size}px;
                color: #333;
                padding: 10px;
            }}
        """)

        # 提示用户字体大小已更改
        self.append_message("系统", f"字体大小已调整为 {self.font_size}px")

    # mousePressEvent 方法现在应该在 change_font_size 之后
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
    app.setStyle('Fusion')
    assistant = PPTAssistant()
    sys.exit(app.exec_())