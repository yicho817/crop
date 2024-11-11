from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np

# 定義數據預處理（不含正規化）
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# 加載數據集
dataset = datasets.ImageFolder('your_dataset_path', transform=transform)
loader = DataLoader(dataset, batch_size=64, shuffle=False, num_workers=4)

# 計算均值和標準差
mean = 0.0
std = 0.0
for images, _ in loader:
    batch_samples = images.size(0)  # batch size (64)
    images = images.view(batch_samples, images.size(1), -1)
    mean += images.mean(2).sum(0)
    std += images.std(2).sum(0)

mean /= len(loader.dataset)
std /= len(loader.dataset)

print("Dataset Mean:", mean)
print("Dataset Std:", std)
