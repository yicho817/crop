import random

# 假設你有一個列表 data
data = list(range(1, 301))  # 假設有 300 個元素

def get_random_chunks(data, chunk_size=50):
    """
    This function yields random chunks of a specified size from the input list.
    The elements in the chunks are unique and do not repeat.
    
    Args:
    data (list): The input list from which to draw elements.
    chunk_size (int): The size of each chunk.
    
    Yields:
    list: A chunk of randomly selected elements.
    """
    data_copy = data[:]  # Create a copy of the data to avoid modifying the original list
    random.shuffle(data_copy)  # Randomly shuffle the list

    # Iterate over the shuffled list in chunks of the specified size
    for i in range(0, len(data_copy), chunk_size):
        yield data_copy[i:i + chunk_size]

# 使用這個函數
for chunk in get_random_chunks(data, 50):
    print(chunk)  # 或者你可以在這裡處理這些數據塊
