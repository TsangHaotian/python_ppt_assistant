import os
import sys
import time


import easyocr
import keyboard
import pyautogui
import pyttsx3
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTextEdit, QDialog, QHBoxLayout
from openai import OpenAI


class AISettingsDialog(QDialog):
    def __init__(self, parent=None, current_prompt=""):
        super().__init__(parent)
        self.setWindowTitle("AI角色设定")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # 添加提示文本
        prompt_label = QLabel("请输入AI角色设定（系统提示词）:")
        layout.addWidget(prompt_label)

        # 添加文本编辑框
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setText(current_prompt)
        layout.addWidget(self.prompt_edit)

        # 移除API Key输入框

        # 添加确认按钮
        confirm_btn = QPushButton("确认")
        # noinspection PyUnresolvedReferences
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

        self.setLayout(layout)

    def get_prompt(self):
        return self.prompt_edit.toPlainText()


# 移除语音识别相关的导入
# 删除以下导入：
# import speech_recognition as sr
# import threading
# from pydub import AudioSegment
# from pydub.silence import split_on_silence

# 在文件顶部添加新的导入
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class PPTAssistant(QWidget):
    def __init__(self):
        super().__init__()
    
        # 初始化资源目录
        self.resource_dir = self.get_resource_path()
    
        # 初始化语音引擎
        self.dragPosition = None
        self.send_btn = QPushButton("发送")
        self.user_input = QTextEdit()
        self.bubble_animation = None
        self.bubble_effect = None
        self.response_bubble = None
        self.close_btn = None
        self.ocr_result_label = None
        self.ai_settings_btn = None
        self.capture_btn = None
        self.character_image = None
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # 设置语速
        self.engine.setProperty('volume', 0.9)  # 设置音量

        # 修改OCR初始化为延迟加载
        self.reader = None
        self.ocr_available = False

        # 初始化AI设置
        self.ai_prompt = "你就是苏轼，你直接代替苏轼的口吻和用户对话，加上一些属于苏轼的语气，不需要任何多余的交互，语言简洁一点，你就是苏轼（你现在的历史时期在你被贬黄州作词定风波的时候）"
        self.api_key = "sk-11f1178aba3548369a489252be37829b"  # 直接使用内置API Key
        self.ai_client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        # 设置窗口属性
        self.setWindowTitle('PPT讲解助手')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建UI元素
        self.initUI()

        # 设置按键监听
        keyboard.add_hotkey('f2', self.process_screen)  # 使用F2键作为触发键，可以根据需要修改

        # 显示窗口
        self.show()

    def get_resource_path(self):
        """获取资源文件路径"""
        try:
            # PyInstaller创建的临时文件夹
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return base_path

    def initUI(self):
        # 创建主布局
        main_layout = QHBoxLayout()

        # 左侧布局 - 动画人物
        left_layout = QVBoxLayout()
        self.character_image = QLabel(self)
        # 修改图片加载方式
        character_path = os.path.join(self.resource_dir, "character.png")
        if not os.path.exists(character_path):
            character_path = os.path.join(self.resource_dir, "C:/Users/Tsang/Pictures/character.png")
        
        self.character_image.setPixmap(
            QPixmap(character_path).scaled(150, 150, Qt.KeepAspectRatio))
        left_layout.addWidget(self.character_image)
        left_layout.addStretch()

        # 右侧布局 - 功能区域
        right_layout = QVBoxLayout()

        # 删除气泡对话框相关代码

        # 创建按钮区域
        button_layout = QHBoxLayout()

        # 截图按钮
        self.capture_btn = QPushButton("召唤苏轼")
        self.capture_btn.setStyleSheet("padding: 8px;")
        button_layout.addWidget(self.capture_btn)

        # AI设置按钮
        self.ai_settings_btn = QPushButton("AI设置")
        self.ai_settings_btn.setStyleSheet("padding: 8px;")
        button_layout.addWidget(self.ai_settings_btn)


        right_layout.addLayout(button_layout)

        # 识别结果显示区域
        self.ocr_result_label = QLabel("等待识别...")
        self.ocr_result_label.setFont(QFont('Arial', 9))
        self.ocr_result_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 120);
                padding: 8px;
                border-radius: 5px;
                max-height: 60px;
            }
        """)
        self.ocr_result_label.setWordWrap(True)
        right_layout.addWidget(self.ocr_result_label)

        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.setStyleSheet("padding: 8px;")
        button_layout.addWidget(self.close_btn)

        # 组合布局
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # 连接按钮信号
        # noinspection PyUnresolvedReferences
        self.capture_btn.clicked.connect(self.process_screen)
        # noinspection PyUnresolvedReferences
        self.ai_settings_btn.clicked.connect(self.open_ai_settings)
        # noinspection PyUnresolvedReferences
        self.close_btn.clicked.connect(self.close)

        # 设置窗口大小
        self.resize(500, 250)
        self.setMinimumSize(400, 200)

        # 创建气泡对话框效果
        self.response_bubble = QLabel()
        self.response_bubble.setFont(QFont('Arial', 10))
        self.response_bubble.setStyleSheet("""
            QLabel {
                color: black;
                background-color: white;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ddd;
                min-width: 200px;
                max-width: 250px;
            }
            QLabel:after {
                content: "";
                position: absolute;
                width: 0;
                height: 0;
                border-left: 10px solid white;
                border-right: 10px solid transparent;
                border-top: 10px solid transparent;
                border-bottom: 10px solid transparent;
                right: -20px;
                top: 20px;
            }
        """)
        self.response_bubble.setWordWrap(True)
        self.response_bubble.setAlignment(Qt.AlignLeft)

        # 添加气泡动画效果
        self.bubble_effect = QGraphicsOpacityEffect()
        self.bubble_effect.setOpacity(0)
        self.response_bubble.setGraphicsEffect(self.bubble_effect)

        # 创建动画
        self.bubble_animation = QPropertyAnimation(self.bubble_effect, b"opacity")
        self.bubble_animation.setDuration(500)
        self.bubble_animation.setStartValue(0)
        self.bubble_animation.setEndValue(1)

        right_layout.addWidget(self.response_bubble)
        right_layout.addStretch()

        # 添加其他控件
        right_layout.addWidget(self.ocr_result_label)
        right_layout.addWidget(self.capture_btn)
        right_layout.addWidget(self.ai_settings_btn)
        right_layout.addWidget(self.close_btn)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # 调整窗口大小
        self.resize(450, 350)

        # 在右侧布局中添加用户输入区域
        self.user_input.setPlaceholderText("在这里输入您的问题...")
        self.user_input.setMaximumHeight(80)
        right_layout.addWidget(self.user_input)

        # 添加发送按钮
        self.send_btn.setStyleSheet("padding: 8px;")
        # noinspection PyUnresolvedReferences
        self.send_btn.clicked.connect(self.handle_user_input)
        right_layout.addWidget(self.send_btn)

    def handle_user_input(self):
        """处理用户输入"""
        user_text = self.user_input.toPlainText().strip()
        if user_text:
            self.get_ai_response(user_text)
            self.user_input.clear()

    def get_ai_response(self, text):
        """获取AI回复并朗读"""
        try:
            # 显示"思考中..."提示
            self.show_bubble_reply("思考中...")
            self.ocr_result_label.setText("正在处理...")

            # 使用线程获取AI回复
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.ai_prompt},
                    {"role": "user", "content": text},
                ],
                max_tokens=500,
                stream=True  # 启用流式响应
            )

            # 逐步显示回复内容
            full_reply = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    part = chunk.choices[0].delta.content
                    full_reply += part
                    self.show_bubble_reply(full_reply)
                    QApplication.processEvents()
                    time.sleep(0.05)

            # 更新状态为识别完成
            self.ocr_result_label.setText("识别完成")

            # 朗读AI回复
            self.engine.say(full_reply)
            self.engine.runAndWait()

            return full_reply

        except Exception as e:
            error_msg = f"AI响应错误: {str(e)}"
            self.show_bubble_reply(error_msg)
            self.ocr_result_label.setText("识别失败")
            return error_msg

    def show_bubble_reply(self, text):
        """显示气泡回复"""
        self.response_bubble.setText(text)
        self.bubble_animation.start()

        # 自动调整气泡大小
        self.response_bubble.adjustSize()
        max_width = 250
        if self.response_bubble.width() > max_width:
            self.response_bubble.setFixedWidth(max_width)

    def open_ai_settings(self):
        """打开AI设置对话框"""
        dialog = AISettingsDialog(self, self.ai_prompt)
        if dialog.exec_():
            self.ai_prompt = dialog.get_prompt()
            self.response_bubble.setText("AI角色设定已更新")  # 修改为response_bubble

    def init_ocr(self):
        """延迟初始化OCR"""
        if self.reader is None:
            try:
                print("正在加载OCR引擎，首次运行可能需要下载模型...")
                # 减少不必要的语言包
                self.reader = easyocr.Reader(['ch_sim'], gpu=False, model_storage_directory=os.path.join(self.resource_dir, 'models'))
                self.ocr_available = True
                print("OCR引擎加载完成，使用CPU模式")
            except Exception as e:
                print(f"OCR引擎加载失败: {str(e)}")
                self.ocr_available = False

    def process_screen(self):
        try:
            # 首次使用时初始化OCR
            if self.reader is None:
                self.init_ocr()
                
            # 显示"正在识别..."提示
            self.show_bubble_reply("正在识别...")

            # 暂时隐藏窗口，避免截图中包含自己
            self.hide()
            time.sleep(0.1)  # 减少等待时间

            # 截取屏幕
            screenshot = pyautogui.screenshot()

            # 显示窗口
            self.show()

            # 保存截图到临时文件
            temp_file = os.path.join(os.environ['TEMP'], 'ppt_screenshot.png')
            screenshot.save(temp_file, quality=50)  # 降低图片质量提高速度

            # 使用EasyOCR进行识别
            try:
                if self.ocr_available:
                    # 使用更快的识别参数
                    results = self.reader.readtext(temp_file,
                                                   batch_size=1,  # 减少批处理大小
                                                   detail=0)  # 只返回文本

                    text = ' '.join(results) if results else "未识别到文本内容"
                else:
                    text = "OCR引擎未正确加载"

                # 显示识别结果
                self.show_bubble_reply(f"识别完成: {text[:50]}...")

                # 获取AI回复
                if text and text != "未识别到文本内容" and text != "OCR引擎未正确加载":
                    return self.get_ai_response(text)

            except Exception as ocr_error:
                print(f"OCR识别错误: {str(ocr_error)}")
                self.show_bubble_reply(f"识别失败: {str(ocr_error)}")

            # 删除临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)

        except Exception as e:
            self.show_bubble_reply(f"识别错误: {str(e)}")
            self.show()  # 确保窗口显示

    def mousePressEvent(self, event):
        # 实现窗口拖动
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 实现窗口拖动
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    assistant = PPTAssistant()
    sys.exit(app.exec_())