import cv2
import numpy as np
import matplotlib.pyplot as plt

# 讀取影像
image_path = 'your_image.jpg'  # 替換為你的影像路徑
original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# 將影像像素值正規化到 0 到 1 之間
normalized_image = cv2.normalize(original_image, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

# 顯示原始影像和正規化後影像
plt.figure(figsize=(10, 5))

# 原始影像
plt.subplot(1, 2, 1)
plt.imshow(original_image, cmap='gray')
plt.title('Original Image')
plt.axis('off')

# 正規化後影像
plt.subplot(1, 2, 2)
plt.imshow(normalized_image, cmap='gray')
plt.title('Normalized Image')
plt.axis('off')

plt.show()
