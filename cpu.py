import requests
from bs4 import BeautifulSoup

def fetch_cpu_terms(url):
    # 送出HTTP GET請求到指定URL
    response = requests.get(url)
    
    # 確認請求成功
    if response.status_code == 200:
        # 解析HTML內容
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取所有的詞條
        terms = soup.find_all('li')
        cpu_terms = []
        for term in terms:
            text = term.get_text()
            if 'CPU' in text or 'processor' in text:
                cpu_terms.append(text)
        
        return cpu_terms
    else:
        print("Failed to retrieve the page.")
        return []

# 維基百科URL（可根據需要更換其他網站）
url = 'https://en.wikipedia.org/wiki/List_of_CPU_architectures'

# 獲取CPU專有名詞列表
cpu_terms = fetch_cpu_terms(url)

# 顯示結果
for term in cpu_terms:
    print(term)
