import cv2
import numpy as np

# 載入原始圖片和偏移後的圖片
img1 = cv2.imread('original.jpg')
img2 = cv2.imread('shifted.jpg')

# 將圖片轉換為灰階
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# 使用 ORB 檢測特徵點和描述符
orb = cv2.ORB_create()
kp1, des1 = orb.detectAndCompute(gray1, None)
kp2, des2 = orb.detectAndCompute(gray2, None)

# 使用 BFMatcher 匹配特徵點
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)

# 排序匹配點
matches = sorted(matches, key=lambda x: x.distance)

# 取得匹配點的座標
src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

# 計算仿射變換矩陣
M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)

# 從矩陣提取偏移量和旋轉角度
tx = M[0, 2]
ty = M[1, 2]
angle = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi

print(f"偏移量: x = {tx}, y = {ty}")
print(f"旋轉角度: {angle} 度")
