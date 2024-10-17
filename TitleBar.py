import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPoint

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(self.palette().Highlight)

        self.close_button = QPushButton("X", self)
        self.close_button.clicked.connect(self.close_window)
        self.close_button.setStyleSheet("background-color: red; color: white; border: none;")

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(QLabel("Custom Title Bar"))
        self.layout.addStretch()
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)

        self.startPos = None

    def close_window(self):
        self.window().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPos = event.globalPos()
            self.clickPos = self.mapToParent(event.pos())

    def mouseMoveEvent(self, event):
        if self.startPos:
            self.window().move(event.globalPos() - self.clickPos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPos = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 設置視窗無邊框
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 創建主窗口小部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 創建自定義標題欄
        self.title_bar = CustomTitleBar(self)

        # 設置樣式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #A9A9A9; /* 視窗背景顏色 */
            }
            QWidget#CustomTitleBar {
                background-color: #008CBA; /* 標題欄背景顏色 */
            }
        """)

        # 設置佈局
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.title_bar)
        self.layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
