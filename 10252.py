import os
import shutil
from datetime import datetime

def list_first_level_folders(root_path):
    """
    列出 root_path 下所有第1層資料夾名稱。
    
    :param root_path: str, 根資料夾路徑
    :return: list, 第1層資料夾名稱的清單
    """
    folders = []
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path):
            folders.append(item_path)
    return folders

def find_latest_date_folder(root_path, target_depth):
    """
    找到指定層級中最新的日期資料夾（假設日期格式為 YYYYMMDD）。
    
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
                if dirname.isdigit() and len(dirname) == 8:
                    try:
                        folder_date = datetime.strptime(dirname, "%Y%m%d")
                        if latest_date is None or folder_date > latest_date:
                            latest_date = folder_date
                            latest_folder = os.path.join(dirpath, dirname)
                    except ValueError:
                        continue
    return latest_folder

def copy_and_rename_all(src_root, dest_root):
    """
    將 src_root 下所有符合條件的資料夾複製到目標路徑。
    
    :param src_root: str, 來源根資料夾路徑
    :param dest_root: str, 目標根資料夾路徑
    """
    # 掃描 src_root 中的所有第1層資料夾
    first_level_folders = list_first_level_folders(src_root)
    
    for folder_path in first_level_folders:
        path_parts = folder_path.split(os.sep)
        
        # 檢查是否至少有3層
        if len(path_parts) < 3:
            print(f"Skipping {folder_path}: Not enough levels.")
            continue
        
        bbb_name = path_parts[1]
        ccc_name = path_parts[2]
        new_folder_name = f"{bbb_name}_{ccc_name}"
        
        # 第一次搜尋最新日期資料夾（第4層）
        latest_folder_level_4 = find_latest_date_folder(folder_path, 4)
        if not latest_folder_level_4:
            print(f"No valid date folder found at level 4 in {folder_path}.")
            continue
        
        # 第二次搜尋最新日期資料夾（第7層）
        latest_folder_level_7 = find_latest_date_folder(latest_folder_level_4, 7)
        if not latest_folder_level_7:
            print(f"No valid date folder found at level 7 in {latest_folder_level_4}.")
            continue
        
        # 建立目標路徑
        new_dest_path = os.path.join(dest_root, new_folder_name)
        
        # 複製資料夾
        shutil.copytree(latest_folder_level_7, new_dest_path, dirs_exist_ok=True)
        print(f"Copied: {latest_folder_level_7} -> {new_dest_path}")

# Example usage
src_root = r'C:\Source\AAA'  # 根資料夾路徑
dest_root = r'C:\Destination\Backup'  # 目標路徑

copy_and_rename_all(src_root, dest_root)
