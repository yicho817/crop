import sys
import os
import cv2
import glob
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QProgressBar, QTableWidget, QTableWidgetItem, QScrollArea,
    QCheckBox, QGroupBox, QTextBrowser
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from crop import crop_p, process_images_with_cv2
from match import match_golden

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
        self.setGeometry(100, 100, 1280, 800)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        self.stackedWidget = QStackedWidget()
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignHCenter)
        # # Image table
        # self.imageTable = QTableWidget(0, 2)  # 設置表格有2列
        # self.imageTable.setHorizontalHeaderLabels(["Filename", "Image"])
        self.imageTable = QTableWidget()
        self.imageTable.setIconSize(QSize(330, 330))  # 設定縮圖大小
        self.imageTable.setSelectionBehavior(QTableWidget.SelectItems)
        self.imageTable.setSelectionMode(QTableWidget.MultiSelection)
        self.stackedWidget.addWidget(self.imageLabel)
        self.stackedWidget.addWidget(self.imageTable)

        right_layout = QVBoxLayout()

        # Label selector with checkboxes
        self.label_group = QGroupBox("Select Class ID")
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

        # Result label
        self.resultLabel = QTextBrowser()

        # Progress bar
        self.progressBar = QProgressBar()

        btn_w = 150
        btn_h = 50
        load_cropBtn.setFixedSize(btn_w,btn_h)
        self.label_group.setFixedWidth(btn_w)
        self.cropBtn.setFixedSize(btn_w,btn_h)
        loadBtn.setFixedSize(btn_w,btn_h)
        self.trainBtn.setFixedSize(btn_w,btn_h)
        self.inferBtn.setFixedSize(btn_w,btn_h)
        self.resultLabel.setFixedHeight(btn_w)

        right_layout.addWidget(load_cropBtn)
        right_layout.addWidget(self.label_group)
        right_layout.addWidget(self.cropBtn)
        right_layout.addWidget(loadBtn)
        right_layout.addWidget(self.trainBtn)
        right_layout.addWidget(self.inferBtn)

        right_layout.addStretch()

        top_layout.addLayout(right_layout)
        top_layout.addWidget(self.stackedWidget)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.progressBar)
        main_layout.addWidget(self.resultLabel)

        self.setLayout(main_layout)

    def load_crop_images(self):
        # image_folder_path = r"D:\OK"
        # sample_name = r"20240520130236-P1516640-20-H-SPGT24139001205.jpg"
        # label_name = r"20240520130236-P1516640-20-H-SPGT24139001205.txt"
        # classes_name = r"classes.txt"

        self.stackedWidget.setCurrentWidget(self.imageLabel)
        image_path_new, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not image_path_new:
            return
        self.image_path = image_path_new
        self.image_folder_path = os.path.dirname(self.image_path)
        img_name_full = os.path.basename(self.image_path)
        self.image_name = os.path.splitext(img_name_full)[0]
        self.label_name = self.image_name+".txt"
        self.classes_name = "classes.txt"
        self.label_path = os.path.join(self.image_folder_path, self.image_name+".txt")
        self.classes_path = os.path.join(self.image_folder_path, "classes.txt")
        if os.path.exists(self.label_path) and os.path.exists(self.classes_path):
            # Read image
            self.image = cv2.imread(self.image_path)
            original_height, original_width, _ = self.image.shape

            # scale image
            self.imageLabel.setAlignment(Qt.AlignHCenter)
            qlabel_size = self.imageLabel.size()
            scale_w = qlabel_size.width() / original_width
            scale_h = qlabel_size.height() / original_height
            scale_factor = min(scale_w, scale_h)

            self.new_width = int(original_width * scale_factor)
            self.new_height = int(original_height * scale_factor)

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
            self.update_label_checkboxes_class_id()
            self.cropBtn.setDisabled(False)
            self.resultLabel.append("Crop Image ready. Please select Label to crop")
        else:
            self.resultLabel.append("Label or Class file not found.")

    def update_label_checkboxes_class_id(self):
        self.clear_checkboxes()
        self.show_image_with_yolo()
        for class_id in self.present_class_ids:
            if class_id < len(self.classes):
                class_name = self.classes[class_id]
                checkbox = QCheckBox(class_name)
                checkbox.setProperty("class_id", class_id)
                checkbox.stateChanged.connect(self.update_image_with_selected_labels)
                self.label_checkboxes.append(checkbox)
                self.label_layout.addWidget(checkbox)

    def get_select_label_class_id(self):
        select_label_class_id = []
        for checkbox in self.label_checkboxes:
            if checkbox.isChecked():
                class_id = checkbox.property("class_id")
                select_label_class_id.append(class_id)
        return select_label_class_id

    def get_select_label_from_class_id(self):
        select_label_yolo = []
        selected_labels = self.get_select_label_class_id()
        for yolo_line in self.yolo_lines:
            parts = yolo_line.strip().split()
            class_id = int(parts[0])
            if class_id not in selected_labels:
                continue
            select_label_yolo.append(yolo_line)
        return select_label_yolo

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
        select_label_yolo = []
        for checkbox in self.label_checkboxes:
            if checkbox.isChecked():
                yolo_line = checkbox.property("yolo_line")
                select_label_yolo.append(yolo_line)
        return select_label_yolo

    def get_select_label(self):
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
        return select_label

    def update_image_with_selected_labels(self):
        selected_labels = [checkbox for checkbox in self.label_checkboxes if checkbox.isChecked()]

        if selected_labels:
            for checkbox in self.label_checkboxes:
                if checkbox in selected_labels:
                    self.class_name = checkbox.text()
                else:
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
        self.show_image_with_yolo()

    def selected_labels_with_yolo(self, parts, label, new_width, new_height, resized_image):
        x_center, y_center, w, h = map(float, parts[1:])

        # 計算實際邊框位置
        x1 = int((x_center - w / 2) * new_width)
        y1 = int((y_center - h / 2) * new_height)
        x2 = int((x_center + w / 2) * new_width)
        y2 = int((y_center + h / 2) * new_height)

        # 繪製邊框與標籤
        cv2.rectangle(resized_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.putText(resized_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return resized_image


    def show_image_with_yolo(self):
        # selected_labels = self.get_select_label_yolo()
        selected_labels = self.get_select_label_from_class_id()
        yolo_image = cv2.resize(self.image, (self.new_width, self.new_height), interpolation=cv2.INTER_AREA)
        # for line in self.yolo_lines:
        for line in selected_labels:
            parts = line.strip().split()
            class_id = int(parts[0])
            label = self.classes[class_id] if class_id < len(self.classes) else f"Class {class_id}"
            yolo_image = self.selected_labels_with_yolo(parts, label, self.new_width, self.new_height, yolo_image)

        # 將處理後的圖片顯示在 QLabel 上
        self.display_image(yolo_image)

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
        # select_labels = self.get_select_label_yolo()
        selected_labels = self.get_select_label_from_class_id()

        # if not selected_labels:
        #     self.resultLabel.append("Please select at least one labels.")
        #     return

        self.resultLabel.append("Start Crop")
        QApplication.processEvents()
        # target_paths = glob.glob(os.path.join(self.image_folder_path, "*.jpg"))

        # output_folder_path = os.path.join(image_folder_path, "output")
        output_folder_path = r"output"
        os.makedirs(output_folder_path, exist_ok=True)

        output_golden_path = os.path.join(output_folder_path, "golden")
        os.makedirs(output_golden_path, exist_ok=True)

        class_count = {}

        for yolo_line in selected_labels:
            parts = yolo_line.strip().split()
            class_id = int(parts[0])
            class_name = self.classes[int(class_id)]
            if class_name in class_count:
                class_count[class_name] += 1
            else:
                class_count[class_name] = 1

            # Crop golden sample
            golden_pic = crop_p(self.image, yolo_line, scale=1)

            # 儲存或顯示裁剪後的圖像
            golden_pic_path = os.path.join(output_golden_path, f"{class_name}_{str(class_count[class_name])}.jpg")
            cv2.imwrite(golden_pic_path, golden_pic)
            print(f"Saved: {golden_pic_path}")
            self.resultLabel.append(f"Saved: {golden_pic_path}")
            QApplication.processEvents()

            # Crop Big sample
            for original_target_img, target_path in process_images_with_cv2(self.image_folder_path):
            # for target_path in target_paths:
                target_pic = crop_p(original_target_img, yolo_line, scale=1.5)
                print(f"Crop: {target_path}")
                self.resultLabel.append(f"Crop: {target_path}")
                QApplication.processEvents()
                output_target_path = os.path.join(output_folder_path, class_name)
                os.makedirs(output_target_path, exist_ok=True)
                match_image = match_golden(output_target_path, golden_pic, target_pic)
                # 儲存剪下的圖片
                original_img_name = os.path.basename(target_path)
                img_name = os.path.splitext(original_img_name)[0]
                cropped_image_name = os.path.join(output_target_path, f'{class_name}_{str(class_count[class_name])}_{img_name}_crop.jpg')
                cv2.imwrite(cropped_image_name, match_image)
                print(f"Saved: {cropped_image_name}")
                self.resultLabel.append(f"Saved: {cropped_image_name}")
                QApplication.processEvents()

        self.resultLabel.append("Crop Finish")
        folder = r"output"
        file_path = os.path.join(folder, self.class_name)
        self.update_image_table(file_path)

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
                icon = QIcon(pixmap.scaled(330, 330, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 縮放圖片
                # image_item = QTableWidgetItem(icon, file_name)
                image_item = QTableWidgetItem(icon, "")
                image_item.setData(Qt.UserRole, file_path)

                self.imageTable.setItem(row_position, col_position, image_item)
                self.imageTable.setColumnWidth(col_position, 400)
                self.imageTable.setRowHeight(row_position, 400)
                col_position +=1

        # 自動調整列寬度以適應內容
        self.imageTable.resizeColumnsToContents()
        self.imageTable.resizeRowsToContents()
        self.stackedWidget.setCurrentWidget(self.imageTable)
        self.trainBtn.setDisabled(False)
        # self.imageTable.selectionMode(self.update_selected_images_display)

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

    def update_selected_images_display(self):
        select_images = self.get_selected_images()
        if select_images:
            select_images_text = "\n".join([os.path.basename(img) for img in select_images])
            self.resultLabel.setText(f"Selected Image:\n{select_images_text}")
        else:
            self.resultLabel.setText(f"No Selected Image")


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
        self.resultLabel.append("\n".join(results))

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ImageGallery()
    ex.show()
    sys.exit(app.exec_())

