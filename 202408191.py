import cv2

# 讀取圖片和標註文件
image_path = "path/to/your/image.jpg"
label_path = "path/to/your/label.txt"

image = cv2.imread(image_path)
height, width, _ = image.shape

# 讀取YOLO格式的標註
with open(label_path, "r") as file:
    lines = file.readlines()

# 處理每一個標註
for line in lines:
    # 解析標註
    class_id, x_center, y_center, bbox_width, bbox_height = map(float, line.split())
    
    # 計算實際像素座標
    x_center *= width
    y_center *= height
    bbox_width *= width
    bbox_height *= height
    
    # 計算邊界框的左上角和右下角座標
    x_min = int(x_center - bbox_width / 2)
    y_min = int(y_center - bbox_height / 2)
    x_max = int(x_center + bbox_width / 2)
    y_max = int(y_center + bbox_height / 2)
    
    # 裁剪圖像
    cropped_image = image[y_min:y_max, x_min:x_max]
    
    # 儲存或顯示裁剪後的圖像
    cropped_image_path = f"cropped_{int(class_id)}.jpg"
    cv2.imwrite(cropped_image_path, cropped_image)
    print(f"Saved: {cropped_image_path}")

