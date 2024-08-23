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
