import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QProgressBar, QTableWidget, QTableWidgetItem, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from crop import crop_pic


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
        self.image_paths = []
        self.current_index = 0

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Gallery Selector")
        self.setGeometry(100, 100, 1400, 800)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # # Image table
        # self.imageTable = QTableWidget(0, 2)  # 設置表格有2列
        # self.imageTable.setHorizontalHeaderLabels(["Filename", "Image"])
        # self.imageTable.setIconSize(QSize(128, 128))  # 設定縮圖大小
        # self.imageTable.setSelectionBehavior(QTableWidget.SelectRows)
        # self.imageTable.setSelectionMode(QTableWidget.MultiSelection)
        # self.imageLabel = QLabel()
        # self.imageLabel.setAlignment(Qt.AlignHCenter)

        self.stackedWidget = QStackedWidget()
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignHCenter)
        self.imageTable = QTableWidget(0, 2)
        self.imageTable.setIconSize(QSize(256, 256))  # 設定縮圖大小
        self.imageTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.imageTable.setSelectionMode(QTableWidget.MultiSelection)
        self.stackedWidget.addWidget(self.imageLabel)
        self.stackedWidget.addWidget(self.imageTable)

        right_layout = QVBoxLayout()

        # Load Crop images button
        load_cropBtn = QPushButton("Load Crop Image")
        load_cropBtn.clicked.connect(self.load_crop_images)

        # Crop button
        cropBtn = QPushButton("Crop Images")
        cropBtn.clicked.connect(self.crop_images)

        # Load images button
        loadBtn = QPushButton("Load Images")
        loadBtn.clicked.connect(self.load_images)

        # Train button
        trainBtn = QPushButton("Send for Training")
        trainBtn.clicked.connect(self.send_for_training)

        # Inference button
        self.inferBtn = QPushButton("Send for Inference")
        self.inferBtn.clicked.connect(self.send_for_inference)
        self.inferBtn.setDisabled(True)

        load_cropBtn.setMaximumWidth(150)
        cropBtn.setMaximumWidth(150)
        loadBtn.setMaximumWidth(150)
        trainBtn.setMaximumWidth(150)
        self.inferBtn.setMaximumWidth(150)

        top_layout.addWidget(self.stackedWidget)
        right_layout.addWidget(load_cropBtn)
        right_layout.addWidget(cropBtn)
        right_layout.addWidget(loadBtn)
        right_layout.addWidget(trainBtn)
        right_layout.addWidget(self.inferBtn)

        right_layout.addStretch()

        top_layout.addLayout(right_layout)
        main_layout.addLayout(top_layout)

        # Progress bar
        self.progressBar = QProgressBar()
        main_layout.addWidget(self.progressBar)

        # Result label
        self.resultLabel = QLabel()
        main_layout.addWidget(self.resultLabel)

        self.setLayout(main_layout)


    def load_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            # self.image_paths = [
            #     os.path.join(folder, file_name) for file_name in os.listdir(folder)
            #     if file_name.endswith(('.png', '.jpg', '.jpeg'))
            # ]
            for file_name in os.listdir(folder):
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(folder, file_name)
                    row_position = self.imageTable.rowCount()
                    self.imageTable.insertRow(row_position)

                    # 將圖片縮圖加到表格
                    pixmap = QPixmap(file_path)
                    icon = QIcon(pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 縮放圖片
                    image_item = QTableWidgetItem(icon, "")
                    image_item.setData(Qt.UserRole, file_path)
                    self.imageTable.setItem(row_position, 1, image_item)

                    # 加入檔名
                    filename_item = QTableWidgetItem(file_name)
                    self.imageTable.setItem(row_position, 0, filename_item)
                    self.imageTable.setRowHeight(row_position, 256)

            # 自動調整列寬度以適應內容
            self.imageTable.resizeColumnsToContents()
            self.stackedWidget.setCurrentWidget(self.imageTable)

    def load_crop_images(self):
        # image_folder_path = r"D:\OK"
        # sample_name = r"20240520130236-P1516640-20-H-SPGT24139001205.jpg"
        # label_name = r"20240520130236-P1516640-20-H-SPGT24139001205.txt"
        # classes_name = r"classes.txt"
        # crop_pic(image_folder_path, sample_name, label_name, classes_name)
        # selected_images = self.get_selected_images()
        # if not selected_images:
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not self.image_path:
            return
        # else:
        #     image_path = selected_images

        self.image_folder_path = os.path.dirname(self.image_path)
        img_name_full = os.path.basename(self.image_path)
        self.image_name = os.path.splitext(img_name_full)[0]
        self.label_name = self.image_name+".txt"
        self.classes_name = "classes.txt"
        self.label_path = os.path.join(self.image_folder_path, self.image_name+".txt")
        self.classes_path = os.path.join(self.image_folder_path, "classes.txt")


        if os.path.exists(self.label_path) and os.path.exists(self.classes_path):
            self.show_image_with_yolo()
        else:
            self.resultLabel.setText("Label or Class file not found.")

    def show_image_with_yolo(self):
        # 讀取圖片
        image = cv2.imread(self.image_path)
        original_height, original_width, _ = image.shape


        # 縮放圖片
        self.imageLabel.setAlignment(Qt.AlignHCenter)
        qlabel_size = self.imageLabel.size()
        scale_w = qlabel_size.width() / original_width
        scale_h = qlabel_size.height() / original_height
        scale_factor = min(scale_w, scale_h)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # 讀取類別名稱
        with open(self.classes_path, 'r') as cf:
            classes = [line.strip() for line in cf.readlines()]

        # 讀取 YOLO 標籤並繪製邊框
        with open(self.label_path, 'r') as lf:
            for line in lf:
                parts = line.strip().split()
                class_id = int(parts[0])
                x_center, y_center, w, h = map(float, parts[1:])

                # 計算實際邊框位置
                x1 = int((x_center - w / 2) * new_width)
                y1 = int((y_center - h / 2) * new_height)
                x2 = int((x_center + w / 2) * new_width)
                y2 = int((y_center + h / 2) * new_height)

                # 繪製邊框與標籤
                cv2.rectangle(resized_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                label = classes[class_id] if class_id < len(classes) else f"Class {class_id}"
                cv2.putText(resized_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 將處理後的圖片顯示在 QLabel 上
        self.display_image(resized_image)

    def display_image(self, image):
        # 將 OpenCV 圖片轉換為 QPixmap
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self.imageLabel.setPixmap(pixmap)
        self.stackedWidget.setCurrentWidget(self.imageLabel)


    # def display_image(self, image):
    #     # 將 OpenCV 圖片轉換為 QPixmap
    #     height, width, channel = image.shape
    #     bytes_per_line = 3 * width
    #     q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    #     pixmap = QPixmap.fromImage(q_img)

    #     # 縮放圖片以適應 QLabel，但保持長寬比例
    #     scaled_pixmap = pixmap.scaled(
    #         self.imageLabel.size(),
    #         Qt.KeepAspectRatio,
    #         Qt.SmoothTransformation
    #     )

    #     # 將縮放後的圖片顯示在 QLabel 上
    #     self.imageLabel.setPixmap(scaled_pixmap)


    def crop_images(self):
        # image_folder_path = r"D:\OK"
        # sample_name = r"20240520130236-P1516640-20-H-SPGT24139001205.jpg"
        # label_name = r"20240520130236-P1516640-20-H-SPGT24139001205.txt"
        # classes_name = r"classes.txt"
        # crop_pic(image_folder_path, sample_name, label_name, classes_name)
        # selected_images = self.get_selected_images()
        # if not selected_images:
        # image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        # if not image_path:
        #     return
        # # else:
        # #     image_path = selected_images

        # image_folder_path = os.path.dirname(image_path)
        # img_name_full = os.path.basename(image_path)
        # image_name = os.path.splitext(img_name_full)[0]
        # # label_name = os.path.join(image_folder_path, image_name+".txt")
        # # classes_name = os.path.join(image_folder_path, "classes.txt")
        # label_name = image_name+".txt"
        # classes_name = "classes.txt"
        folder = r"output"

        if os.path.exists(self.label_path) and os.path.exists(self.classes_path):
            crop_pic(self.image_folder_path, self.image_path, self.label_name, self.classes_name)
            self.imageLabel.clear()
            self.imageLabel.setDisabled(True)
            self.resultLabel.setText("Crop Finish")
            self.imageTable.setDisabled(False)
            self.imageTable.setRowCount(0)  # 清空表格內容
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                row_position = self.imageTable.rowCount()
                self.imageTable.insertRow(row_position)

                # 加入檔名
                filename_item = QTableWidgetItem(file_name)
                self.imageTable.setItem(row_position, 0, filename_item)

                # 將圖片縮圖加到表格
                pixmap = QPixmap(file_path)
                icon = QIcon(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 縮放圖片
                image_item = QTableWidgetItem(icon, "")
                image_item.setData(Qt.UserRole, file_path)
                self.imageTable.setItem(row_position, 1, image_item)
                self.imageTable.setRowHeight(row_position, 128)
            # 自動調整列寬度以適應內容
            self.imageTable.resizeColumnsToContents()
        else:
            self.resultLabel.setText("Label or Class file not found.")


    def send_for_training(self):
        # selected_images = self.get_selected_images()
        # if selected_images:
        #     self.process_images(selected_images, "training")
        self.inferBtn.setDisabled(False)

    def send_for_inference(self):
        # selected_images = self.get_selected_images()
        # if selected_images:
        #     self.process_images(selected_images, "inference")
        pass

    def get_selected_images(self):
        selected_items = self.imageTable.selectedItems()
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

