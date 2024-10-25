import os
import shutil
from datetime import datetime

def get_latest_date_folder(root_path):
    """
    遍歷多層資料夾，找到最新的日期資料夾（假設日期格式為YYYYMMDD）。
    
    :param root_path: str, 根資料夾路徑
    :return: tuple, (最新日期資料夾的完整路徑, BBB與CCC資料夾名稱)
    """
    latest_folder = None
    latest_date = None
    bbb_name = ''
    ccc_name = ''
    
    # 遍歷所有子資料夾
    for dirpath, dirnames, filenames in os.walk(root_path):
        # 分割資料夾路徑，提取每一層的名稱
        path_parts = dirpath.split(os.sep)
        
        # 假設 BBB 是第2層, CCC 是第3層
        if len(path_parts) >= 3:
            bbb_name = path_parts[1]  # 提取 BBB
            ccc_name = path_parts[2]  # 提取 CCC
        
        for dirname in dirnames:
            # 檢查資料夾名稱是否為日期格式（YYYYMMDD）
            if dirname.isdigit() and len(dirname) == 8:
                try:
                    # 轉換資料夾名稱為日期
                    folder_date = datetime.strptime(dirname, "%Y%m%d")
                    
                    # 比較日期，找出最新的資料夾
                    if latest_date is None or folder_date > latest_date:
                        latest_date = folder_date
                        latest_folder = os.path.join(dirpath, dirname)
                except ValueError:
                    continue
    
    return latest_folder, bbb_name, ccc_name

def copy_and_rename(src_root, dest_root):
    """
    複製AAA資料夾內最新的日期資料夾，並將資料夾名稱轉換為指定名稱。
    
    :param src_root: str, 來源資料夾根路徑
    :param dest_root: str, 目標資料夾根路徑
    """
    # 找到最新的日期資料夾，以及BBB和CCC名稱
    latest_date_folder, bbb_name, ccc_name = get_latest_date_folder(src_root)

    if latest_date_folder:
        # 組合新的資料夾名稱為 'BBB_CCC'
        new_folder_name = f'{bbb_name}_{ccc_name}'
        
        # 建立目標路徑，將名稱轉換為指定的資料夾名稱
        new_dest_path = os.path.join(dest_root, new_folder_name)
        
        # 檢查目標路徑是否存在，若不存在則建立
        if not os.path.exists(new_dest_path):
            os.makedirs(new_dest_path)
        
        # 複製整個資料夾
        shutil.copytree(latest_date_folder, new_dest_path, dirs_exist_ok=True)
        print(f"Copied: {latest_date_folder} -> {new_dest_path}")
    else:
        print("No valid date folder found!")

# Example usage
src_root = r'C:\Source\AAA'  # 根資料夾 AAA
dest_root = r'C:\Destination\Backup'  # 目標資料夾

copy_and_rename(src_root, dest_root)
