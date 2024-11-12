import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt

# 讀取影像
image_path = 'your_image.jpg'  # 替換為你的影像路徑
original_image = Image.open(image_path).convert('RGB')

# 轉換成 tensor 並顯示原始影像
to_tensor = transforms.ToTensor()
image_tensor = to_tensor(original_image)

# 定義 Normalize 的 mean 和 std (假設 mean 和 std 是針對 ImageNet 的平均值)
mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]

# 定義標準化轉換
normalize = transforms.Normalize(mean=mean, std=std)
normalized_image_tensor = normalize(image_tensor)

# 將標準化後的 tensor 轉換回影像格式 (為了顯示)
def tensor_to_image(tensor):
    tensor = tensor.clone().detach()
    tensor = tensor * torch.tensor(std).view(3, 1, 1) + torch.tensor(mean).view(3, 1, 1)  # 反向標準化
    tensor = torch.clamp(tensor, 0, 1)  # 限制到 0 到 1 的範圍
    return transforms.ToPILImage()(tensor)

# 顯示原始影像和標準化後影像
plt.figure(figsize=(10, 5))

# 原始影像
plt.subplot(1, 2, 1)
plt.imshow(original_image)
plt.title('Original Image')
plt.axis('off')

# 標準化後影像
plt.subplot(1, 2, 2)
plt.imshow(tensor_to_image(normalized_image_tensor))
plt.title('Normalized Image')
plt.axis('off')

plt.show()
