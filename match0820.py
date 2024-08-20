import cv2

# 讀取原始圖片和目標圖片
original_image = cv2.imread('original_image.jpg')
target_image = cv2.imread('target_image.jpg')

# 確認圖片讀取成功
if original_image is None or target_image is None:
    print("Error: One of the images could not be loaded.")
    exit()

# 將圖片轉換為灰度
gray_original = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
gray_target = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

# 進行模板匹配
result = cv2.matchTemplate(gray_original, gray_target, cv2.TM_CCOEFF_NORMED)

# 找到最佳匹配的位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# 獲取目標圖片的尺寸
h, w = target_image.shape[:2]

# 使用最佳匹配的位置來計算範圍
top_left = max_loc
bottom_right = (top_left[0] + w, top_left[1] + h)

# 確保範圍在原始圖片的邊界內
top_left = (max(top_left[0], 0), max(top_left[1], 0))
bottom_right = (min(bottom_right[0], original_image.shape[1]), min(bottom_right[1], original_image.shape[0]))

# 剪下對應區域
cropped_image = original_image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

# 儲存剪下的圖片
cv2.imwrite('cropped_image.jpg', cropped_image)

# 顯示結果
cv2.imshow('Cropped Image', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
