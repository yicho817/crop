import re
from difflib import SequenceMatcher

# 定義一個函式來計算字串相似度
def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 根據型號、微架構名稱或縮寫來搜尋對應的縮寫及功率
def find_most_similar_abbreviation_and_power(target_str, dictionaries):
    most_similar_abbreviation = None
    highest_similarity = 0
    power = None

    # 檢查是否為型號和功率，例如 H28 -> 28W
    match = re.search(r'H(\d+)', target_str)  # 假設型號的功率在 H 後面
    if match:
        power = f"{match.group(1)}W"  # 提取並格式化功率

    # 先檢查是否直接匹配型號
    for d in dictionaries:
        for model, model_power in d.get("models", {}).items():
            if target_str in model:
                # 確保優先選擇微架構名稱，如果匹配到型號，返回微架構縮寫
                if most_similar_abbreviation and most_similar_abbreviation != d.get("name"):
                    continue
                return d.get("name", ""), model_power  # 返回縮寫和功率

    # 如果型號不匹配，則檢查是否匹配微架構名稱或縮寫
    for d in dictionaries:
        description = d.get("description", "")
        similarity = string_similarity(target_str, description)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_abbreviation = d.get("name", "")
    
    # 如果找到了相應的微架構，並且有提取功率
    return most_similar_abbreviation, power if power else highest_similarity

# 測試範例
target_str = "i9-13900"  # 測試 "MTL", "Ryzen 5 5600X", "H28"
most_similar_abbreviation, result = find_most_similar_abbreviation_and_power(target_str, dictionaries)

print("最相似的縮寫:", most_similar_abbreviation)
print("結果:", result)
