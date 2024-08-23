def load_images(self):
    folder = QFileDialog.getExistingDirectory(self, "Select Folder")
    if folder:
        self.imageTable.setRowCount(0)  # 清空表格內容
        self.imageTable.setIconSize(QSize(256, 256))  # 設置縮圖大小，這裡設定為 256x256

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
                self.imageTable.setItem(row_position, 0, image_item)

                # 加入檔名
                filename_item = QTableWidgetItem(file_name)
                self.imageTable.setItem(row_position, 1, filename_item)

        # 自動調整列寬度以適應內容
        self.imageTable.resizeColumnsToContents()





    def load_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not image_path:
            return

        folder = os.path.dirname(image_path)
        label_file = os.path.splitext(image_path)[0] + ".txt"  # 假設標籤檔名與圖片檔名一致
        class_file = os.path.join(folder, "classes.txt")

        if os.path.exists(label_file) and os.path.exists(class_file):
            self.show_image_with_yolo(image_path, label_file, class_file)
        else:
            self.resultLabel.setText("Label or class file not found.")

    def show_image_with_yolo(self, image_path, label_file, class_file):
        # 讀取圖片
        image = cv2.imread(image_path)
        height, width, _ = image.shape

        # 讀取類別名稱
        with open(class_file, 'r') as cf:
            classes = [line.strip() for line in cf.readlines()]

        # 讀取 YOLO 標籤並繪製邊框
        with open(label_file, 'r') as lf:
            for line in lf:
                parts = line.strip().split()
                class_id = int(parts[0])
                x_center, y_center, w, h = map(float, parts[1:])

                # 計算實際邊框位置
                x1 = int((x_center - w / 2) * width)
                y1 = int((y_center - h / 2) * height)
                x2 = int((x_center + w / 2) * width)
                y2 = int((y_center + h / 2) * height)

                # 繪製邊框與標籤
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = classes[class_id] if class_id < len(classes) else f"Class {class_id}"
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # 將處理後的圖片顯示在 QLabel 上
        self.display_image(image)

    def display_image(self, image):
        # 將 OpenCV 圖片轉換為 QPixmap
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QPixmap(QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped())
        self.imageLabel.setPixmap(q_img)
        self.imageLabel.adjustSize()



def display_image(self, image):
    # 將 OpenCV 圖片轉換為 QPixmap
    height, width, channel = image.shape
    bytes_per_line = 3 * width
    q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    pixmap = QPixmap.fromImage(q_img)
    
    # 縮放圖片以適應 QLabel，但保持長寬比例
    scaled_pixmap = pixmap.scaled(
        self.imageLabel.size(), 
        Qt.KeepAspectRatio, 
        Qt.SmoothTransformation
    )

    # 將縮放後的圖片顯示在 QLabel 上
    self.imageLabel.setPixmap(scaled_pixmap)

