import requests
import json

# 测试 API 返回的中文
response = requests.get("http://localhost:3000/api/observations/test-chinese-20260227195756")
data = response.json()

if data:
    print("观察记录内容:")
    for obs in data:
        print(f"  {obs['content']}")
        
    # 检查是否有乱码
    if any('�' in obs['content'] for obs in data):
        print("\nERROR: 检测到乱码")
    else:
        print("\nOK: 中文显示正常")
else:
    print("没有观察记录")
