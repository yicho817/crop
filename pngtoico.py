from PIL import Image

def png_to_ico(png_path, ico_path):
    # 打開PNG圖像
    image = Image.open(png_path)
    
    # 將PNG圖像轉換為ICO格式並保存
    image.save(ico_path, format='ICO')

if __name__ == "__main__":
    # 設定PNG圖像路徑
    png_path = "path/to/your/image.png"  # 修改為你的PNG文件路徑
    
    # 設定要保存的ICO圖像路徑
    ico_path = "path/to/save/image.ico"  # 修改為你要保存的ICO文件路徑
    
    # 進行轉換
    png_to_ico(png_path, ico_path)

    print("Conversion completed.")
