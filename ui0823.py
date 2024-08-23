import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QProgressBar
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
import cv2

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

        # Image table
        self.imageTable = QTableWidget(0, 2)  # 設置表格有2列
        self.imageTable.setHorizontalHeaderLabels(["Image", "Filename"])
        self.imageTable.setIconSize(QSize(128, 128))  # 設定縮圖大小
        self.imageTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.imageTable.setSelectionMode(QTableWidget.MultiSelection)
        layout.addWidget(self.imageTable)

        # Load images button
        loadBtn = QPushButton("Load Images")
        loadBtn.clicked.connect(self.load_images)
        layout.addWidget(loadBtn)

        # Crop Image button
        cropBtn = QPushButton("Crop Image")
        cropBtn.clicked.connect(self.crop_image)
        layout.addWidget(cropBtn)

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
            self.imageTable.setRowCount(0)  # 清空表格內容
            for file_name in os.listdir(folder):
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(folder, file_name)
                    row_position = self.imageTable.rowCount()
                    self.imageTable.insertRow(row_position)

                    # 將圖片加到表格
                    icon = QIcon(file_path)
                    image_item = QTableWidgetItem(icon, "")
                    image_item.setData(Qt.UserRole, file_path)
                    self.imageTable.setItem(row_position, 0, image_item)

                    # 加入檔名
                    filename_item = QTableWidgetItem(file_name)
                    self.imageTable.setItem(row_position, 1, filename_item)

    def crop_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not image_path:
            return

        folder = os.path.dirname(image_path)
        label_file = os.path.join(folder, "label.txt")
        class_file = os.path.join(folder, "classes.txt")

        if os.path.exists(label_file) and os.path.exists(class_file):
            self.process_crop(image_path, label_file, class_file)
        else:
            self.resultLabel.setText("Label or class file not found.")

    def process_crop(self, image_path, label_file, class_file):
        image = cv2.imread(image_path)

        with open(label_file, 'r') as lf, open(class_file, 'r') as cf:
            labels = lf.readlines()
            classes = cf.readlines()

        self.resultLabel.setText(f"Cropped image from {image_path} using {label_file} and {class_file}")

    def send_for_training(self):
        selected_images = self.get_selected_images()
        if selected_images:
            self.process_images(selected_images, "training")

    def send_for_inference(self):
        selected_images = self.get_selected_images()
        if selected_images:
            self.process_images(selected_images, "inference")

    def get_selected_images(self):
        selected_images = []
        selected_rows = self.imageTable.selectionModel().selectedRows()
        for row in selected_rows:
            image_item = self.imageTable.item(row.row(), 0)
            selected_images.append(image_item.data(Qt.UserRole))
        return selected_images

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









import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QProgressBar
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
import cv2

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

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)
        self._scale_factor = 1.0

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update_display()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._scale_factor *= 1.1  # 放大
        else:
            self._scale_factor /= 1.1  # 縮小
        self.update_display()

    def update_display(self):
        if self._pixmap:
            scaled_pixmap = self._pixmap.scaled(
                self._pixmap.size() * self._scale_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)

class ImageGallery(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Gallery Selector")
        self.setGeometry(100, 100, 800, 600)

        layout = QHBoxLayout()

        # Image display area
        self.imageLabel = ImageLabel(self)
        layout.addWidget(self.imageLabel)

        # Button layout
        rightLayout = QVBoxLayout()

        loadBtn = QPushButton("Load Image")
        loadBtn.clicked.connect(self.load_image)
        rightLayout.addWidget(loadBtn)

        cropBtn = QPushButton("Crop Image")
        cropBtn.clicked.connect(self.crop_image)
        rightLayout.addWidget(cropBtn)

        trainBtn = QPushButton("Send for Training")
        trainBtn.clicked.connect(self.send_for_training)
        rightLayout.addWidget(trainBtn)

        inferBtn = QPushButton("Send for Inference")
        inferBtn.clicked.connect(self.send_for_inference)
        rightLayout.addWidget(inferBtn)

        # Progress bar and result label
        self.progressBar = QProgressBar()
        rightLayout.addWidget(self.progressBar)

        self.resultLabel = QLabel()
        rightLayout.addWidget(self.resultLabel)

        layout.addLayout(rightLayout)
        self.setLayout(layout)

    def load_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not image_path:
            return

        folder = os.path.dirname(image_path)
        label_file = os.path.join(folder, "label.txt")
        class_file = os.path.join(folder, "classes.txt")

        if os.path.exists(label_file) and os.path.exists(class_file):
            self.show_image_with_yolo(image_path, label_file, class_file)
        else:
            self.resultLabel.setText("Label or class file not found.")

    def show_image_with_yolo(self, image_path, label_file, class_file):
        image = cv2.imread(image_path)
        original_height, original_width, _ = image.shape

        # 縮放圖片
        qlabel_size = self.imageLabel.size()
        scale_w = qlabel_size.width() / original_width
        scale_h = qlabel_size.height() / original_height
        scale_factor = min(scale_w, scale_h)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        with open(class_file, 'r') as cf:
            classes = [line.strip() for line in cf.readlines()]

        with open(label_file, 'r') as lf:
            for line in lf:
                parts = line.strip().split()
                class_id = int(parts[0])
                x_center, y_center, w, h = map(float, parts[1:])

                x1 = int((x_center - w / 2) * new_width)
                y1 = int((y_center - h / 2) * new_height)
                x2 = int((x_center + w / 2) * new_width)
                y2 = int((y_center + h / 2) * new_height)

                cv2.rectangle(resized_image, (x1, y1), (x2, y2), (0, 255, 0), 4)
                label = classes[class_id] if class_id < len(classes) else f"Class {class_id}"
                cv2.putText(resized_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        self.display_image(resized_image)

    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self.imageLabel.setPixmap(pixmap)

    def crop_image(self):
        pass

    def send_for_training(self):
        pass

    def send_for_inference(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageGallery()
    ex.show()
    sys.exit(app.exec_())

