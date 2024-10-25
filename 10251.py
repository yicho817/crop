import os
import shutil
from datetime import datetime

def find_latest_date_folder(root_path, target_depth):
    """
    遍歷指定層級，找到最新的日期資料夾（假設日期格式為YYYYMMDD）。
    
    :param root_path: str, 根資料夾路徑
    :param target_depth: int, 目標層級（從根資料夾開始計算）
    :return: str, 最新日期資料夾的完整路徑
    """
    latest_folder = None
    latest_date = None
    
    for dirpath, dirnames, _ in os.walk(root_path):
        # 計算目前資料夾的層級
        depth = len(dirpath.split(os.sep)) - len(root_path.split(os.sep)) + 1
        
        if depth == target_depth:
            for dirname in dirnames:
                # 檢查資料夾名稱是否為日期格式（YYYYMMDD）
                if dirname.isdigit() and len(dirname) == 8:
                    try:
                        folder_date = datetime.strptime(dirname, "%Y%mdd")
                        
                        # 更新最新日期和路徑
                        if latest_date is None or folder_date > latest_date:
                            latest_date = folder_date
                            latest_folder = os.path.join(dirpath, dirname)
                    except ValueError:
                        continue
    return latest_folder

def copy_and_rename(src_root, dest_root):
    """
    將第4層和第7層的最新日期資料夾複製到目標路徑，並自動命名。

    :param src_root: str, 來源資料夾根路徑
    :param dest_root: str, 目標資料夾根路徑
    """
    # 提取第2層和第3層資料夾名稱來組合目標名稱
    path_parts = src_root.split(os.sep)
    if len(path_parts) < 3:
        print("Source path does not have enough levels.")
        return
    
    bbb_name = path_parts[1]
    ccc_name = path_parts[2]
    new_folder_name = f"{bbb_name}_{ccc_name}"

    # 第一次搜尋最新日期資料夾（第4層）
    latest_folder_level_4 = find_latest_date_folder(src_root, 4)
    if not latest_folder_level_4:
        print("No valid date folder found at level 4.")
        return
    
    # 第二次搜尋最新日期資料夾（第7層，以第4層結果為基準）
    latest_folder_level_7 = find_latest_date_folder(latest_folder_level_4, 7)
    if not latest_folder_level_7:
        print("No valid date folder found at level 7.")
        return
    
    # 建立目標路徑
    new_dest_path = os.path.join(dest_root, new_folder_name)
    
    # 複製資料夾
    shutil.copytree(latest_folder_level_7, new_dest_path, dirs_exist_ok=True)
    print(f"Copied: {latest_folder_level_7} -> {new_dest_path}")

# Example usage
src_root = r'C:\Source\AAA'  # 根資料夾路徑
dest_root = r'C:\Destination\Backup'  # 目標路徑

copy_and_rename(src_root, dest_root)
