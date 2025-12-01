# modelscope_download.py
import os
os.environ['HF_ENDPOINT'] = 'https://mirrors.modelscope.cn'

# 设置缓存路径
cache_dir = "/Users/indexerror/Documents/MyStuff/Projects/VueProjects/bitnp-ai-vtuber/backend/tts/GPT_SoVITS/pretrained_models/fast_langdetect"
os.makedirs(cache_dir, exist_ok=True)
os.environ['FAST_LANGDETECT_CACHE'] = cache_dir

# 现在导入和使用 fast-langdetect
from fast_langdetect import detect

result = detect("这是一个测试文本")
print(f"检测结果: {result}")

# import ssl
# print(ssl.get_default_verify_paths())