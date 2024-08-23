import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QListWidgetItem, QProgressBar
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize

class ImageProcessingThread(QThread):
    progress = pyqtSignal(int)
    result_ready = pyqtSignal(list)

    def __init__(self, images, mode):
        super().__init__()
        self.images = images
        self.mode = mode

    def run(self):
        processed_images = []
        total = len(self.images)
        for i, image_path in enumerate(self.images):
            self.sleep(1)  # 模擬處理過程
            processed_images.append(f"Processed {image_path} in {self.mode} mode")
            self.progress.emit(int((i + 1) / total * 100))
        self.result_ready.emit(processed_images)

class ImageGallery(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Gallery Selector")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Image list
        self.imageList = QListWidget()
        self.imageList.setIconSize(QSize(128, 128))  # 設定縮圖大小
        self.imageList.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.imageList)

        # Load images button
        loadBtn = QPushButton("Load Images")
        loadBtn.clicked.connect(self.load_images)
        layout.addWidget(loadBtn)

        # Train button
        trainBtn = QPushButton("Send for Training")
        trainBtn.clicked.connect(self.send_for_training)
        layout.addWidget(trainBtn)

        # Inference button
        inferBtn = QPushButton("Send for Inference")
        inferBtn.clicked.connect(self.send_for_inference)
        layout.addWidget(inferBtn)

        # Progress bar
        self.progressBar = QProgressBar()
        layout.addWidget(self.progressBar)

        # Result label
        self.resultLabel = QLabel()
        layout.addWidget(self.resultLabel)

        self.setLayout(layout)

    def load_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.imageList.clear()
            for file_name in os.listdir(folder):
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(folder, file_name)
                    item = QListWidgetItem(QIcon(file_path), file_name)
                    item.setData(Qt.UserRole, file_path)
                    self.imageList.addItem(item)

    def send_for_training(self):
        selected_images = self.get_selected_images()
        if selected_images:
            self.process_images(selected_images, "training")

    def send_for_inference(self):
        selected_images = self.get_selected_images()
        if selected_images:
            self.process_images(selected_images, "inference")

    def get_selected_images(self):
        selected_items = self.imageList.selectedItems()
        return [item.data(Qt.UserRole) for item in selected_items]

    def process_images(self, images, mode):
        self.progressBar.setValue(0)
        self.resultLabel.clear()

        self.thread = ImageProcessingThread(images, mode)
        self.thread.progress.connect(self.update_progress)
        self.thread.result_ready.connect(self.show_results)
        self.thread.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def show_results(self, results):
        self.resultLabel.setText("\n".join(results))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageGallery()
    ex.show()
    sys.exit(app.exec_())
