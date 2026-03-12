
# import os
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import shutil
# import json
# import re
# from google import genai
# from google.genai import types
# from background_remover import process_image

# import os
# import sys

# # 🎀 强行指路：告诉 Python 去 src 文件夹找东西
# sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# # ... 后面保持不变 ...
# from background_remover import process_image

# app = FastAPI()

# # 允许跨域
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 初始化新版客户端
# client = genai.Client(api_key="AIzaSyBhCh685tIPX-CKBRjCk3flOmMM5UaVeMM")

# @app.post("/process-item")
# async def process_item(
#     file: UploadFile = File(...),
#     brand_tier: str = Form(...)
# ):
#     # 1. 保存原图
#     os.makedirs("output", exist_ok=True)
#     input_path = f"output/{file.filename}"
#     with open(input_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # 2. 抠图魔法 (Loopy 变白底图)
#     processed_path = process_image(input_path)
#     if not processed_path:
#         processed_path = input_path # 兜底用原图

#     # 3. 让 Gemini 分析 (使用新版 SDK 语法)
#     try:
#         # 上传文件到 Google 服务器（Gemini 1.5 处理图片更准）
#         with open(processed_path, "rb") as f:
#             image_data = f.read()

#         prompt = f"""
#         你现在是 XYLAB 的首席奢侈品鉴定师 Loopy。
#         请分析这张图中的时尚单品（品牌层级: {brand_tier}）。
        
#         必须返回严格的 JSON 格式，不要包含任何 Markdown 标记或文字说明。格式如下：
#         {{
#             "pricing": {{
#                 "fastSale": 120,
#                 "marketValue": 150,
#                 "currency": "USD"
#             }},
#             "descriptions": {{
#                 "poshmark": "文案内容",
#                 "ebay": "文案内容",
#                 "mercari": "文案内容",
#                 "depop": "文案内容"
#             }},
#             "itemDetails": {{
#                 "brand": "识别出的品牌",
#                 "category": "类别",
#                 "condition": "Excellent"
#             }}
#         }}
#         """

#         response = client.models.generate_content(
#             model="gemini-1.5-flash", # 或者 gemini-1.5-flash
#             contents=[
#                 types.Content(
#                     role="user",
#                     parts=[
#                         types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
#                         types.Part.from_text(text=prompt),
#                     ],
#                 ),
#             ],
#         )

#         # 4. 强力 JSON 清洗逻辑
#         raw_text = response.text
#         # 去掉 ```json 和 ``` 标记
#         json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
#         if json_match:
#             result = json.loads(json_match.group())
#         else:
#             raise ValueError("AI 没有返回正确的 JSON 格式")

#         # 确保图片路径返回给前端
#         result["processedImage"] = f"http://localhost:8000/{processed_path}"
        
#         return result

#     except Exception as e:
#         print(f"❌ 后厨出事了: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# # 挂载静态文件，让前端能看到图
# from fastapi.staticfiles import StaticFiles
# app.mount("/output", StaticFiles(directory="output"), name="output")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()

# 允许跨域，方便前端调试
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎀 挂载 output 文件夹，确保前端能通过 http://localhost:8000/output/xxx 访问到图
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.post("/process-item")
async def process_item(
    file: UploadFile = File(...),
    brand_tier: str = Form(...)
):
    try:
        # 1. 模拟处理延迟（让你能看两秒 Loopy 的优雅视频，调 UI 必备）
        # 如果追求极致速度，可以把下面这行注释掉
        import time
        time.sleep(2) 

        # 2. 🎀 UI 调试核心：直接指向你 output 文件夹里那张完美的白底图
        # 请确保 output 文件夹里确实有这张图，或者改成你现有的文件名
        mock_processed_image = "http://localhost:8000/output/IMG_8842_processed.jpg"

        # 3. 返回一套完美的“名媛级” Mock 数据
        return {
            "pricing": {
                "fastSale": 850,
                "marketValue": 1200,
                "currency": "USD"
            },
            "descriptions": {
                "poshmark": "✨ [XYLAB SELECT] Rare find! This piece perfectly embodies the STANCE CORE aesthetic. Immaculate condition, professionally authenticated. 🎀",
                "ebay": "Authentic Luxury Item. Excellent pre-owned condition. Ships with original dustbag. Part of the XYLAB premium resale collection.",
                "mercari": "Super cute and high-end! ✨ Only worn twice. Open to reasonable offers from fellow Loopy fans! 🎀",
                "depop": "Vintage luxury vibes. Stance core style. 100% authentic. DM for world wide shipping! 💎 #XYLAB #Luxe"
            },
            "itemDetails": {
                "brand": "Designer Luxury",
                "category": "High-End Accessory",
                "condition": "Pristine / Like New"
            },
            "processedImage": mock_processed_image
        }

    except Exception as e:
        print(f"❌ UI Mock Server 出错了: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)