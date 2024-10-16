import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMessageBox, QListWidget, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        self.setScaledContents(True)
        self.image = None
        self.current_pixmap = None
        self.rect_start = None
        self.rect_end = None
        self.cropping = False

    def set_image(self, image):
        self.image = image
        self.display_image()

    def display_image(self):
        qformat = QImage.Format_Indexed8
        if len(self.image.shape) == 3:  
            if self.image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(self.image, self.image.shape[1], self.image.shape[0], self.image.strides[0], qformat)
        img = img.rgbSwapped()

        self.current_pixmap = QPixmap.fromImage(img)
        self.setPixmap(self.current_pixmap)
        self.resize(self.current_pixmap.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None:
            self.rect_start = self.get_image_coordinates(event.pos())
            self.cropping = True

    def mouseMoveEvent(self, event):
        if self.cropping and self.image is not None:
            self.rect_end = self.get_image_coordinates(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.cropping:
            self.rect_end = self.get_image_coordinates(event.pos())
            self.cropping = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.image is not None:
            self.setPixmap(self.current_pixmap.copy())
            if self.rect_start and self.rect_end:
                painter = QPainter(self.pixmap())
                pen = QPen(Qt.red, 2, Qt.SolidLine)
                painter.setPen(pen)
                rect = QRect(self.rect_start, self.rect_end)
                painter.drawRect(rect)
                painter.end()
                self.update()

    def get_image_coordinates(self, pos):
        label_width = self.width()
        label_height = self.height()
        pixmap_width = self.current_pixmap.width()
        pixmap_height = self.current_pixmap.height()

        x_ratio = pixmap_width / label_width
        y_ratio = pixmap_height / label_height

        x = int(pos.x() * x_ratio)
        y = int(pos.y() * y_ratio)

        x = max(0, min(x, pixmap_width))
        y = max(0, min(y, pixmap_height))

        return QPoint(x, y)

    def get_crop_coordinates(self):
        if self.rect_start and self.rect_end:
            x_min = min(self.rect_start.x(), self.rect_end.x())
            y_min = min(self.rect_start.y(), self.rect_end.y())
            x_max = max(self.rect_start.x(), self.rect_end.x())
            y_max = max(self.rect_start.y(), self.rect_end.y())
            return x_min, y_min, x_max, y_max
        return None

### 主窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Cropping Tool")
        self.setGeometry(100, 100, 1000, 600)

        self.open_button = QPushButton("Open Folder", self)
        self.open_button.clicked.connect(self.open_folder)
        self.open_button.setMaximumWidth(200)

        self.file_list = QListWidget(self)
        self.file_list.itemClicked.connect(self.load_image)
        self.file_list.setMaximumWidth(200)

        self.mark_button = QPushButton("Rect Box", self)
        self.mark_button.setEnabled(False)
        self.mark_button.clicked.connect(self.enable_marking)
        self.mark_button.setMaximumWidth(200)

        self.save_button = QPushButton("Crop and Save", self)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_crop)
        self.save_button.setMaximumWidth(200)

        self.image_label = ImageLabel(self)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.open_button)
        left_layout.addWidget(self.file_list)
        left_layout.addWidget(self.mark_button)
        left_layout.addWidget(self.save_button)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.scroll_area, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.scroll_area.setMinimumWidth(600)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_list.clear()
            image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            for image_file in image_files:
                self.file_list.addItem(os.path.join(folder_path, image_file))

    def load_image(self, item):
        self.image_path = item.text()
        if self.image_path:
            image = cv2.imread(self.image_path)
            self.image_label.set_image(image)
            self.mark_button.setEnabled(True)

    def enable_marking(self):
        self.image_label.rect_start = None
        self.image_label.rect_end = None
        self.image_label.cropping = False
        self.save_button.setEnabled(False)
        self.image_label.update()

    def save_crop(self):
        crop_coords = self.image_label.get_crop_coordinates()
        if crop_coords:
            x_min, y_min, x_max, y_max = crop_coords
            cropped_img = self.image_label.image[y_min:y_max, x_min:x_max]

            save_path, _ = QFileDialog.getSaveFileName(self, "Save Cropped Image", "", "Image Files (*.png *.jpg *.jpeg)")
            if save_path:
                cv2.imwrite(save_path, cropped_img)
                QMessageBox.information(self, "Save Successful", f"Cropped image saved as: {save_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
