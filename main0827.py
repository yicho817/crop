import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QProgressBar, QTableWidget, QTableWidgetItem, QScrollArea,
    QCheckBox, QGroupBox
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
        self.label_checkboxes = []

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
        self.imageTable = QTableWidget()
        self.imageTable.setIconSize(QSize(384, 384))  # 設定縮圖大小
        self.imageTable.setSelectionBehavior(QTableWidget.SelectItems)
        self.imageTable.setSelectionMode(QTableWidget.MultiSelection)
        self.stackedWidget.addWidget(self.imageLabel)
        self.stackedWidget.addWidget(self.imageTable)

        right_layout = QVBoxLayout()

        # Label selector with checkboxes
        self.label_group = QGroupBox("Select Labels")
        self.label_layout = QVBoxLayout()
        self.label_group.setLayout(self.label_layout)

        # Load Crop images button
        load_cropBtn = QPushButton("Load Crop Image")
        load_cropBtn.clicked.connect(self.load_crop_images)

        # Crop button
        self.cropBtn = QPushButton("Crop Images")
        self.cropBtn.clicked.connect(self.crop_images)
        self.cropBtn.setDisabled(True)

        # Load images button
        loadBtn = QPushButton("Load Sample Images")
        loadBtn.clicked.connect(self.load_sample_images)

        # Train button
        self.trainBtn = QPushButton("Send for Training")
        self.trainBtn.clicked.connect(self.send_for_training)
        self.trainBtn.setDisabled(True)

        # Inference button
        self.inferBtn = QPushButton("Send for Inference")
        self.inferBtn.clicked.connect(self.send_for_inference)
        self.inferBtn.setDisabled(True)

        load_cropBtn.setMaximumWidth(150)
        self.cropBtn.setMaximumWidth(150)
        loadBtn.setMaximumWidth(150)
        self.trainBtn.setMaximumWidth(150)
        self.inferBtn.setMaximumWidth(150)

        top_layout.addWidget(self.stackedWidget)
        right_layout.addWidget(load_cropBtn)
        right_layout.addWidget(self.label_group)
        right_layout.addWidget(self.cropBtn)
        right_layout.addWidget(loadBtn)
        right_layout.addWidget(self.trainBtn)
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

    def load_crop_images(self):
        # image_folder_path = r"D:\OK"
        # sample_name = r"20240520130236-P1516640-20-H-SPGT24139001205.jpg"
        # label_name = r"20240520130236-P1516640-20-H-SPGT24139001205.txt"
        # classes_name = r"classes.txt"

        # selected_images = self.get_selected_images()
        # if not selected_images:
        self.stackedWidget.setCurrentWidget(self.imageLabel)
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not self.image_path:
            return

        self.image_folder_path = os.path.dirname(self.image_path)
        img_name_full = os.path.basename(self.image_path)
        self.image_name = os.path.splitext(img_name_full)[0]
        self.label_name = self.image_name+".txt"
        self.classes_name = "classes.txt"
        self.label_path = os.path.join(self.image_folder_path, self.image_name+".txt")
        self.classes_path = os.path.join(self.image_folder_path, "classes.txt")
        if os.path.exists(self.label_path) and os.path.exists(self.classes_path):
            # 讀取類別名稱
            with open(self.classes_path, 'r') as cf:
                self.classes = [line.strip() for line in cf.readlines()]

            # 讀取 YOLO 標籤並繪製邊框
            self.present_class_ids = set()
            with open(self.label_path, 'r') as lf:
                self.yolo_lines = lf.readlines()
                for yolo_line in self.yolo_lines:
                    parts = yolo_line.strip().split()
                    class_id = int(parts[0])
                    self.present_class_ids.add(class_id)
            self.update_label_checkboxes_yolo()
            self.show_image_with_yolo()
            self.cropBtn.setDisabled(False)
            self.resultLabel.setText("Crop Image ready. Please select Label to crop")
        else:
            self.resultLabel.setText("Label or Class file not found.")

    def update_label_checkboxes_yolo(self):
        self.clear_checkboxes()
        for yolo_line in self.yolo_lines:
            parts = yolo_line.strip().split()
            class_id = int(parts[0])
            label = self.classes[class_id] if class_id < len(self.classes) else f"Class {class_id}"
            checkbox = QCheckBox(label)
            checkbox.setProperty("class_id", class_id)
            checkbox.setProperty("yolo_line", yolo_line)
            # checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_image_with_selected_labels)
            self.label_checkboxes.append(checkbox)
            self.label_layout.addWidget(checkbox)

    def get_select_label_yolo(self):
        select_label = []
        select_label_class_id = []
        select_label_yolo = []
        for checkbox in self.label_checkboxes:
            if checkbox.isChecked():
                class_id = checkbox.property("class_id")
                yolo_line = checkbox.property("yolo_line")
                select_label.append(checkbox.text())
                select_label_class_id.append(class_id)
                select_label_yolo.append(yolo_line)
        return select_label_yolo

    def update_image_with_selected_labels(self):
        selected_labels = [checkbox for checkbox in self.label_checkboxes if checkbox.isChecked()]

        if selected_labels:
            for checkbox in self.label_checkboxes:
                if checkbox not in  selected_labels:
                    checkbox.setDisabled(True)
        else:
            for checkbox in self.label_checkboxes:
                checkbox.setDisabled(False)

        self.show_image_with_yolo()
        # self.show_image_with_yolo(selected_labels)

    def clear_checkboxes(self):
        for checkbox in self.label_checkboxes:
            self.label_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.label_checkboxes = []


    def show_image_with_yolo(self):
        # if selected_labels is None:
        #     selected_labels= [self.classes[int(line.strip().split()[0])] for line in self.yolo_lines]

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

        selected_labels = self.get_select_label_yolo()

        for line in self.yolo_lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            label = self.classes[class_id] if class_id < len(self.classes) else f"Class {class_id}"
            # if selected_labels is None or parts in selected_labels:
            x_center, y_center, w, h = map(float, parts[1:])

            if line not in selected_labels:
                continue

            # 計算實際邊框位置
            x1 = int((x_center - w / 2) * new_width)
            y1 = int((y_center - h / 2) * new_height)
            x2 = int((x_center + w / 2) * new_width)
            y2 = int((y_center + h / 2) * new_height)

            # 繪製邊框與標籤
            cv2.rectangle(resized_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

            cv2.putText(resized_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 將處理後的圖片顯示在 QLabel 上
        self.display_image(resized_image)

    def display_image(self, image):
        # 將 OpenCV 圖片轉換為 QPixmap
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
    #     # 縮放圖片以適應 QLabel，但保持長寬比例
    #     scaled_pixmap = pixmap.scaled(
    #         self.imageLabel.size(),
    #         Qt.KeepAspectRatio,
    #         Qt.SmoothTransformation
    #     )
    #     # 將縮放後的圖片顯示在 QLabel 上
    #     self.imageLabel.setPixmap(scaled_pixmap)
        self.imageLabel.setPixmap(pixmap)
        self.stackedWidget.setCurrentWidget(self.imageLabel)

    def crop_images(self):
        select_labels = self.get_select_label_yolo()
        if not select_labels:
            self.resultLabel.setText("Please select at least one labels.")
            return
        self.resultLabel.setText("Start Crop")
        crop_pic(self.image_folder_path, self.image_path, select_labels, self.classes)
        self.resultLabel.setText("Crop Finish")
        folder = r"output\crop"
        self.update_image_table(folder)

    def update_image_table(self,folder):
        self.stackedWidget.setCurrentWidget(self.imageTable)
        self.imageTable.setRowCount(0)
        self.imageTable.setColumnCount(3)
        row_position = 0
        col_position = 0
        for file_name in os.listdir(folder):
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(folder, file_name)

                if col_position == 3:
                    col_position = 0
                    row_position += 1

                if col_position == 0:
                    self.imageTable.insertRow(row_position)

                # # 加入檔名
                # filename_item = QTableWidgetItem(file_name)
                # self.imageTable.setItem(row_position, 0, filename_item)

                # 將圖片縮圖加到表格
                pixmap = QPixmap(file_path)
                icon = QIcon(pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 縮放圖片
                # image_item = QTableWidgetItem(icon, file_name)
                image_item = QTableWidgetItem(icon, "")
                image_item.setData(Qt.UserRole, file_path)

                self.imageTable.setItem(row_position, col_position, image_item)
                self.imageTable.setColumnWidth(col_position, 512)
                self.imageTable.setRowHeight(row_position, 550)
                col_position +=1

        # 自動調整列寬度以適應內容
        self.imageTable.resizeColumnsToContents()
        self.imageTable.resizeRowsToContents()
        # self.imageTable.setIconSize(QSize(256, 256))  # 設定縮圖大小
        self.stackedWidget.setCurrentWidget(self.imageTable)
        self.trainBtn.setDisabled(False)

    def load_sample_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.update_image_table(folder)

    def send_for_training(self):
        selected_images = self.get_selected_images()
        if selected_images:
            self.process_images(selected_images, "training")
        self.inferBtn.setDisabled(False)

    def send_for_inference(self):
        selected_images = self.get_unselected_images()
        if selected_images:
            self.process_images(selected_images, "inference")
        pass

    def get_selected_images(self):
        selected_items = self.imageTable.selectedItems()
        return [item.data(Qt.UserRole) for item in selected_items]

    def get_unselected_images(self):
        unselected_items =  []
        for row in range(self.imageTable.rowCount()):
            for col in range(self.imageTable.columnCount()):
                item = self.imageTable.item(row, col)
                if item and not item.isSelected():
                    unselected_items.append(item)
        return [item.data(Qt.UserRole) for item in unselected_items]


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

