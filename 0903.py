import sys
import os
import cv2
import glob
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QProgressBar, QTableWidget, QTableWidgetItem, QScrollArea,
    QCheckBox, QGroupBox, QTextBrowser
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QObject
from crop import crop_p, process_images_with_cv2
from match import match_golden
from zip import zip_selected_images


class ImageProcessingThread(QThread):
    progress = pyqtSignal(int)
    result_ready = pyqtSignal(list)

    def __init__(self, images, mode, class_name, main_win):
        super().__init__()
        self.images = images
        self.mode = mode
        self.class_name = class_name
        self.main_win = main_win

    def process_task_crop(self):
        # image_files = glob.glob(os.path.join(images, "*.jpg")) + \
        #             glob.glob(os.path.join(images, "*.png")) + \
        #             glob.glob(os.path.join(images, "*.jpeg"))
        total = len(self.images)
        for i, image_path in enumerate(self.images):
            # img = cv2.imread(file_path)
            # if img is not None:
                # yield img, file_path
            yield image_path
            self.progress.emit(int((i + 1) / total * 100))

    def process_task_training(self, image_path):
        zip_selected_images(image_path, self.class_name + ".zip")
        pass

    def process_task_inference(self, image_path):
        pass

    def run(self):
        processed_images_list = []
        total = len(self.images)
        if self.mode == "Cropping":
            for i, image_path in enumerate(self.images):
                result = [f"Processed {image_path} in {self.mode} mode"]
                # self.result_ready.emit(result)
                processed_images_list.append(result)
                # self.progress.emit(int((i + 1) / total * 100))
        elif self.mode == "Training":
            for i, image_path in enumerate(self.images):
                result = [f"Select {image_path} in {self.mode} mode"]
                self.result_ready.emit(result)
                processed_images_list.append(result)
                self.progress.emit(int((i + 1) / total * 100))
            self.process_task_training(self.images)
            end_result = [f"The images has been packed into {self.class_name}.zip" ]
            self.result_ready.emit(end_result)
        elif self.mode == "Inference":
            for i, image_path in enumerate(self.images):
                self.process_task_inference(image_path)
                result = [f"Processed {image_path} in {self.mode} mode"]
                self.result_ready.emit(result)
            processed_images_list.append(result)
            self.progress.emit(int((i + 1) / total * 100))
        else:
            for i, image_path in enumerate(self.images):
                result = [f"Processed {image_path} in {self.mode} mode"]
                self.result_ready.emit(result)
            processed_images_list.append(result)
            self.progress.emit(int((i + 1) / total * 100))


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(False)
        self._scale_factor = 1.0
        self._pixmap = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._scale_factor = 1.0
        super().setPixmap(pixmap)
        self.adjustSize()
        # self.update_display()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._scale_factor *= 1.1  # 放大
        else:
            self._scale_factor /= 1.1  # 縮小
        self.update_display()

    def update_display(self):
        if self._pixmap:
            # label_size = self.size()
            # pixmap_size = self._pixmap.size()

            scaled_pixmap = self._pixmap.scaled(
                self._pixmap.size() * self._scale_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)
            self.adjustSize()


class ImageCropApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initData()
        self.initUI()

    def initData(self):
        self.label_checkboxes = []
        self.select_label_yolo = []

    def initUI(self):
        self.setWindowTitle("Image Cropping APP")
        self.setGeometry(0, 0, 1000, 600)

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        self.stackedWidget = QStackedWidget()
        self.imageLabel = ImageLabel(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.imageLabel)
        self.scroll_area.setWidgetResizable(True)
        self.imageLabel.setAlignment(Qt.AlignHCenter)
        # # Image table
        # self.imageTable = QTableWidget(0, 2)  # 設置表格有2列
        # self.imageTable.setHorizontalHeaderLabels(["Filename", "Image"])
        self.imageTable = QTableWidget(0,5)
        self.imageTable.setIconSize(QSize(300, 300))  # 設定縮圖大小
        self.imageTable.setSelectionBehavior(QTableWidget.SelectItems)
        self.imageTable.setSelectionMode(QTableWidget.MultiSelection)
        self.stackedWidget.addWidget(self.scroll_area)
        self.stackedWidget.addWidget(self.imageTable)

        control_layout = QVBoxLayout()

        # Label selector with checkboxes
        self.label_group = QGroupBox("Select Class ID", self)
        self.label_layout = QVBoxLayout()
        self.label_group.setLayout(self.label_layout)
        self.scroll_label = QScrollArea(self)
        self.scroll_label.setWidget(self.label_group)
        self.scroll_label.setWidgetResizable(True)
        # Load Crop images button
        load_cropBtn = QPushButton("Load Crop Image", self)
        load_cropBtn.clicked.connect(self.load_crop_images)

        # Crop First button
        self.crop_first_Btn = QPushButton("Preview First Crop", self)
        self.crop_first_Btn.clicked.connect(self.crop_golden_images)
        self.crop_first_Btn.setDisabled(True)

        # Crop All button
        self.crop_all_Btn = QPushButton("Crop All Images", self)
        self.crop_all_Btn.clicked.connect(self.crop_all_images)
        self.crop_all_Btn.setDisabled(True)

        # Load Sample Folder button
        loadBtn = QPushButton("Load Sample Folder", self)
        loadBtn.clicked.connect(self.load_sample_images)

        # Train button
        self.trainBtn = QPushButton("Send for Training", self)
        self.trainBtn.clicked.connect(self.send_for_training)
        self.trainBtn.setDisabled(True)

        # Send Inference button
        self.sendinferBtn = QPushButton("Send for Inference", self)
        self.sendinferBtn.clicked.connect(self.send_for_inference)
        self.sendinferBtn.setDisabled(True)

        # Get Inference button
        self.getinferBtn = QPushButton("Get Inference result", self)
        self.getinferBtn.clicked.connect(self.get_for_inference)
        self.getinferBtn.setDisabled(True)

        # Result label
        self.resultLabel = QTextBrowser(self)

        # Progress bar
        self.progressBar = QProgressBar(self)

        btn_w = 250
        btn_h = 50
        load_cropBtn.setFixedSize(btn_w,btn_h)
        self.scroll_label.setFixedWidth(btn_w)
        self.crop_first_Btn.setFixedSize(btn_w,btn_h)
        self.crop_all_Btn.setFixedSize(btn_w,btn_h)
        loadBtn.setFixedSize(btn_w,btn_h)
        self.trainBtn.setFixedSize(btn_w,btn_h)
        self.sendinferBtn.setFixedSize(btn_w,btn_h)
        self.getinferBtn.setFixedSize(btn_w,btn_h)
        # control_layout.SetMinAndMaxSize( )
        self.stackedWidget.setMaximumSize(1600,900)
        self.resultLabel.setFixedHeight(100)

        control_layout.addWidget(load_cropBtn)
        control_layout.addWidget(self.scroll_label)
        control_layout.addWidget(self.crop_first_Btn)
        control_layout.addWidget(self.crop_all_Btn)
        control_layout.addWidget(loadBtn)
        control_layout.addWidget(self.trainBtn)
        control_layout.addWidget(self.sendinferBtn)
        control_layout.addWidget(self.getinferBtn)

        control_layout.addStretch()

        top_layout.addLayout(control_layout)
        top_layout.addWidget(self.stackedWidget)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.progressBar)
        main_layout.addWidget(self.resultLabel)

        # self.setLayout(main_layout)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_image_and_labels(self, image_path):
        # image_folder_path = r"D:\OK"
        # sample_name = r"20240520130236-P1516640-20-H-SPGT24139001205.jpg"
        # label_name = r"20240520130236-P1516640-20-H-SPGT24139001205.txt"
        # classes_name = r"classes.txt"
        self.image_path = image_path
        self.image_folder_path = os.path.dirname(self.image_path)
        img_name_full = os.path.basename(self.image_path)
        self.image_name = os.path.splitext(img_name_full)[0]
        self.label_name = self.image_name+".txt"
        self.classes_name = "classes.txt"
        self.label_path = os.path.join(self.image_folder_path, self.image_name+".txt")
        self.classes_path = os.path.join(self.image_folder_path, "classes.txt")
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
        # read class name
        with open(self.classes_path, 'r') as cf:
            self.classes = [line.strip() for line in cf.readlines()]
        # read YOLO label
        self.present_class_ids = set()
        with open(self.label_path, 'r') as lf:
            self.yolo_lines = lf.readlines()
            for yolo_line in self.yolo_lines:
                parts = yolo_line.strip().split()
                class_id = int(parts[0])
                self.present_class_ids.add(class_id)

    def load_crop_images(self):
        self.stackedWidget.setCurrentWidget(self.scroll_area)

        image_path_new, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not image_path_new:
            return

        self.load_image_and_labels(image_path_new)

        if os.path.exists(self.label_path) and os.path.exists(self.classes_path):
            self.update_label_checkboxes_class_id()
            self.crop_first_Btn.setDisabled(False)
            self.resultLabel.append("Crop Image ready. Please select Label to crop")
        else:
            self.resultLabel.append("Label or Class file not found.")

    """
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
    """

    def get_select_label_class_id(self):
        select_label_class_id = []
        for checkbox in self.label_checkboxes:
            if checkbox.isChecked():
                class_id = checkbox.property("class_id")
                select_label_class_id.append(class_id)
        return select_label_class_id

    def get_select_label_from_class_id(self):
        self.select_label_yolo = []
        selected_labels = self.get_select_label_class_id()
        for yolo_line in self.yolo_lines:
            parts = yolo_line.strip().split()
            class_id = int(parts[0])
            if class_id not in selected_labels:
                continue
            self.select_label_yolo.append(yolo_line)
        return self.select_label_yolo

    def update_label_checkboxes_class_id(self):
        self.clear_checkboxes()
        # self.show_image_with_yolo()
        for class_id in self.present_class_ids:
            if class_id < len(self.classes):
                class_name = self.classes[class_id]
                checkbox = QCheckBox(class_name)
                checkbox.setProperty("class_id", class_id)
                checkbox.stateChanged.connect(self.update_image_with_selected_labels)
                self.label_checkboxes.append(checkbox)
                self.label_layout.addWidget(checkbox)

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
        # Calculate the actual border position
        x1 = int((x_center - w / 2) * new_width)
        y1 = int((y_center - h / 2) * new_height)
        x2 = int((x_center + w / 2) * new_width)
        y2 = int((y_center + h / 2) * new_height)
        # Draw borders and labels
        cv2.rectangle(resized_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(resized_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return resized_image

    def show_image_with_yolo(self):
        # selected_labels = self.get_select_label_yolo()
        selected_labels = self.get_select_label_from_class_id()
        # selected_labels = self.select_label_yolo
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
        self.stackedWidget.setCurrentWidget(self.scroll_area)

    def crop_golden_image(self, yolo_line, class_count):
        parts = yolo_line.strip().split()
        class_id = int(parts[0])
        class_name = self.classes[int(class_id)]
        class_count[class_name] = class_count.get(class_name, 0) +1
        # Crop golden sample
        golden_pic = crop_p(self.image, yolo_line, scale=1)
        return golden_pic, class_name

    def crop_golden_images(self):
        # select_labels = self.get_select_label_yolo()
        # selected_labels = self.get_select_label_from_class_id()
        selected_labels = self.select_label_yolo
        if not selected_labels:
            self.resultLabel.append("Please select at least one labels.")
            return

        self.output_folder_path = os.path.join(self.image_folder_path, "output")
        self.resultLabel.append("Start Crop")
        class_count = {}
        for yolo_line in selected_labels:
            # Cropped golden image
            golden_pic, class_name = self.crop_golden_image(yolo_line, class_count)
            # Save cropped image
            self.output_target_path = os.path.join(self.output_folder_path, class_name)
            output_golden_path = os.path.join(self.output_target_path, "golden")
            os.makedirs(output_golden_path, exist_ok=True)
            golden_pic_path = os.path.join(self.output_target_path, "golden", f"{class_name}_{str(class_count[class_name])}.jpg")
            cv2.imwrite(golden_pic_path, golden_pic)
            print(f"Saved: {golden_pic_path}")
            self.resultLabel.append(f"Saved: {golden_pic_path}")

        self.resultLabel.append("Crop Finish")
        self.crop_all_Btn.setDisabled(False)
        self.update_image_table(output_golden_path)

    def crop_all_images(self):
        selected_labels = self.select_label_yolo
        self.resultLabel.append("Start Crop")
        QApplication.processEvents()
        # target_paths = glob.glob(os.path.join(self.image_folder_path, "*.jpg"))
        target_paths = glob.glob(os.path.join(self.image_folder_path, "*.jpg")) + \
                    glob.glob(os.path.join(self.image_folder_path, "*.png")) + \
                    glob.glob(os.path.join(self.image_folder_path, "*.jpeg"))
        total = len(target_paths)
        self.progressBar.setMaximum(total)
        # Crop Big sample
        for i, target_path in enumerate(target_paths):
        # for target_path in target_paths:
            class_count = {}
            self.update_image_table(self.output_target_path)
            original_target_img = cv2.imread(target_path)
            for yolo_line in selected_labels:
                print(f"Crop: {target_path}")
                self.resultLabel.append(f"Crop: {target_path}")
                QApplication.processEvents()

                golden_pic, class_name = self.crop_golden_image(yolo_line, class_count)
                target_pic = crop_p(original_target_img, yolo_line, scale=1.5)

                match_image = match_golden(golden_pic, target_pic)

                # Save the cut image
                original_img_name = os.path.basename(target_path)
                img_name = os.path.splitext(original_img_name)[0]
                cropped_image_name = os.path.join(self.output_target_path, f'{class_name}_{str(class_count[class_name])}_{img_name}_crop.jpg')
                cv2.imwrite(cropped_image_name, match_image)
                print(f"Saved: {cropped_image_name}")
                self.resultLabel.append(f"Saved: {cropped_image_name}")
                QApplication.processEvents()
            self.progressBar.setValue(i + 1)
        self.resultLabel.append("Crop Finish")
        self.update_image_table(self.output_target_path)

    def update_image_table(self,folder):
        self.stackedWidget.setCurrentWidget(self.imageTable)
        self.imageTable.setRowCount(0)

        row_position = 0
        col_position = 0
        for file_name in os.listdir(folder):
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(folder, file_name)
                self.imageTable.setColumnCount(5)
                if col_position == 5:
                    col_position = 0
                    row_position += 1

                if col_position == 0:
                    self.imageTable.insertRow(row_position)

                # # 加入檔名
                # filename_item = QTableWidgetItem(file_name)
                # self.imageTable.setItem(row_position, 0, filename_item)

                # 將圖片縮圖加到表格
                pixmap = QPixmap(file_path)
                icon = QIcon(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 縮放圖片
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

    def update_selected_images_display(self):
        select_images = self.get_selected_images()
        if select_images:
            select_images_text = "\n".join([os.path.basename(img) for img in select_images])
            self.resultLabel.setText(f"Selected Image:\n{select_images_text}")
            QApplication.processEvents()
        else:
            self.resultLabel.setText(f"No Selected Image")
            QApplication.processEvents()

    def load_sample_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.update_image_table(folder)
            self.class_name = os.path.basename(folder)

    def send_for_training(self):
        selected_images = self.get_selected_images()
        unselected_images = self.get_unselected_images()
        if selected_images:
            self.process_images(selected_images, "Training")
        self.sendinferBtn.setDisabled(False)

    def send_for_inference(self):
        selected_images = self.get_unselected_images()
        if selected_images:
            self.process_images(selected_images, "Inference")
        self.getinferBtn.setDisabled(False)


    def get_for_inference(self):
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
        # self.resultLabel.clear()

        self.thread = ImageProcessingThread(images, mode, self.class_name, self)
        self.thread.progress.connect(self.update_progress)
        self.thread.result_ready.connect(self.show_results)
        self.thread.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def show_results(self, results):
        self.resultLabel.append("\n".join(results))
        QApplication.processEvents()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ImageCropApp()
    ex.show()
    sys.exit(app.exec_())

