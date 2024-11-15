import numpy as np
import cv2
from torchvision import transforms
from PIL import Image
import torch

# 1. 加載圖像
img_path = 'your_image_path.jpg'  # 替換為你的圖像路徑
image = Image.open(img_path)

# 2. 定義 ImageNet 標準化轉換
normalize = transforms.Compose([
    transforms.ToTensor(),  # 轉換為 Tensor 格式
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 標準化
])

# 3. 應用標準化
normalized_image = normalize(image)

# 4. 將標準化後的圖像從 Tensor 轉換為 NumPy 格式，並調整為 OpenCV 可用的格式
# 注意：cv2 讀取圖像的通道順序是 BGR，而不是 RGB
normalized_image_np = normalized_image.permute(1, 2, 0).numpy()
normalized_image_np = (normalized_image_np * 255).astype(np.uint8)  # 將浮點數轉換為 [0, 255] 範圍
normalized_image_np = cv2.cvtColor(normalized_image_np, cv2.COLOR_RGB2BGR)  # 轉換為 BGR 格式

# 5. 使用 OpenCV 保存標準化後的圖像
cv2.imwrite('imagenet_normalized_image.png', normalized_image_np)
