import os

def scan_and_split_folders(root_path):
    """
    掃描 root_path 下所有資料夾，並根據 root_path 後的層級進行分割。
    
    :param root_path: str, 根資料夾路徑
    :return: list, 每個資料夾路徑的層級結構清單
    """
    folder_levels = []

    for dirpath, dirnames, _ in os.walk(root_path):
        for dirname in dirnames:
            # 完整路徑
            full_path = os.path.join(dirpath, dirname)
            # 分割層級結構
            relative_path = os.path.relpath(full_path, root_path)  # 去掉根路徑的部分
            levels = relative_path.split(os.sep)  # 按資料夾分隔符分割
            folder_levels.append({
                'full_path': full_path,  # 完整路徑
                'levels': levels         # 相對於 root_path 的層級結構
            })
    
    return folder_levels

# Example usage
src_root = r'C:\Source\AAA'  # 根資料夾路徑
all_folders_with_levels = scan_and_split_folders(src_root)

# 顯示每個資料夾的完整路徑和分層級別
for folder in all_folders_with_levels:
    print(f"Full Path: {folder['full_path']}")
    print(f"Levels: {folder['levels']}")
