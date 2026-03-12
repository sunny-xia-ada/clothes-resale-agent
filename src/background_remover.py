

import os
from rembg import remove
from PIL import Image
import io

def process_image(original_filepath, output_folder="output"):
    print("\n" + "🎀" * 15)
    print("Loopy 的魔法工作间：正在全力抠图中... 诶嘿嘿～")
    
    file_name = os.path.basename(original_filepath)
    file_name_no_ext = os.path.splitext(file_name)[0]
    processed_filepath = os.path.join(output_folder, f"{file_name_no_ext}_processed.jpg")

    try:
        with open(original_filepath, "rb") as i:
            input_data = i.read()
            # 施展抠图魔法
            output_data = remove(input_data)
            
            # 检查输出是否为空
            if not output_data or len(output_data) < 100:
                print("⚠️ Loopy 没看清衣服在哪，决定先用原图处理...")
                img = Image.open(original_filepath)
            else:
                img = Image.open(io.BytesIO(output_data))

            # 如果图片是带透明度的 (RGBA)，我们要把它放在白底上
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # 创建一个纯白背景
                white_bg = Image.new("RGB", img.size, (255, 255, 255))
                # 如果是 RGBA，使用 alpha 通道作为遮罩
                if img.mode == 'RGBA':
                    white_bg.paste(img, (0, 0), img)
                else:
                    white_bg.paste(img, (0, 0))
                img = white_bg
            else:
                img = img.convert('RGB')

            # 最终保存
            img.save(processed_filepath, "JPEG", quality=95)
            
        print(f"✅ 魔法成功！白底图已存好: {processed_filepath}")
        return processed_filepath

    except Exception as e:
        print(f"❌ Loopy 尽力了，但魔法还是失灵了: {e}")
        # 如果彻底失败，把原图复制过去充当处理后的图，防止后端卡死
        try:
            shutil.copy(original_filepath, processed_filepath)
            return processed_filepath
        except:
            return None