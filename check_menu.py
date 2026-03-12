

import google.generativeai as genai

# 填入你刚才在终端里用的那个真实的 API Key
genai.configure(api_key="AIzaSyBhCh685tIPX-CKBRjCk3flOmMM5UaVeMM")

print("正在强行索要 Google 内部菜单...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        # 只打印能帮我们生成内容和看图的 AI 模型名字
        print(m.name)