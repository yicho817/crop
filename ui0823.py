import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

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
            print("Training on images:", selected_images)
            # 在這裡處理訓練的邏輯

    def send_for_inference(self):
        selected_images = self.get_selected_images()
        if selected_images:
            print("Inferring on images:", selected_images)
            # 在這裡處理推斷的邏輯

    def get_selected_images(self):
        selected_items = self.imageList.selectedItems()
        return [item.data(Qt.UserRole) for item in selected_items]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageGallery()
    ex.show()
    sys.exit(app.exec_())
