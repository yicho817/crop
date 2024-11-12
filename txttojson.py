
import json

# 初始化變數
json_data = {}
current_title = None

# 讀取 .txt 文件
file_path = 'your_text_file.txt'  # 替換為你的 .txt 文件路徑
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()  # 移除行尾換行符號和多餘空格
        
        # 檢查是否為空白行
        if not line:
            current_title = None  # 重置標題，以便識別下一段標題
            continue
        
        # 檢查是否為新的段落開頭
        if current_title is None:
            current_title = line  # 第一行為標題
        else:
            # 其他行為內容，反向儲存 {內容: 標題}
            json_data[line] = current_title

# 轉換為 JSON 格式並打印
json_output = json.dumps(json_data, ensure_ascii=False, indent=4)
print(json_output)
