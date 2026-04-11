# -*- coding: utf-8 -*-
"""
预览所有测试结果图片 - MBTI风格验证
"""
import sys
import base64
from io import BytesIO

# 导入app.py中的函数
sys.path.insert(0, '.')
from app import generate_label_image, TEST_DATA, get_character_style

def preview_all_result_images():
    """预览所有测试结果图片"""
    print("开始生成所有测试结果图片预览...")
    print("=" * 60)

    # 为每个测试类型生成所有结果的图片
    for test_type, test_data in TEST_DATA.items():
        print(f"\n【{test_data['title']}】")
        print("-" * 60)

        # 按结果键排序，确保显示顺序一致
        sorted_results = sorted(test_data["results"].items())

        for result_key, result_data in sorted_results:
            print(f"\n结果类型: {result_key}")
            print(f"人格标签: {result_data['label']}")
            print(f"全国占比: {result_data['percentage']}")

            try:
                # 获取对应的人物风格
                character_style = get_character_style(test_type, result_key)
                print(f"人物风格: {character_style}")

                # 生成图片（带人物风格）
                img = generate_label_image(result_data["label"], character_style)

                # 保存图片
                filename = f"preview_{test_type}_{result_key}.png"
                img.save(filename)
                print(f"图片已保存: {filename}")

                # 转换为base64用于HTML预览
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()

                # 生成HTML预览代码
                html_code = f'''
                <div style="display: inline-block; margin: 20px; text-align: center;">
                    <img src="data:image/png;base64,{img_base64}" width="400" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);">
                    <p style="color: #e5e7eb; margin-top: 10px; font-size: 14px;">{result_data['label']}</p>
                    <p style="color: #9ca3af; margin-top: 5px; font-size: 12px;">风格: {character_style}</p>
                </div>
                '''

                # 保存HTML预览文件
                with open(f"preview_{test_type}_{result_key}.html", "w", encoding="utf-8") as f:
                    f.write(f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{result_data['label']} - MBTI风格预览</title>
    <style>
        body {{
            background-color: #1a1a2e;
            color: #e5e7eb;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
        }}
        h1 {{
            color: #667eea;
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }}
        .info {{
            margin: 20px 0;
            color: #9ca3af;
        }}
        .style-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{result_data['label']}</h1>
        <div class="info">
            <p>测试类型: {test_data['title']}</p>
            <p>结果代码: {result_key}</p>
            <p>全国占比: {result_data['percentage']}</p>
            <div class="style-tag">风格: {character_style}</div>
        </div>
        {html_code}
    </div>
</body>
</html>
                    ''')

                print(f"HTML预览已生成: preview_{test_type}_{result_key}.html")

            except Exception as e:
                print(f"生成失败: {str(e)}")

    print("\n" + "=" * 60)
    print("所有图片预览生成完成！")
    print("\n使用方法:")
    print("1. 查看PNG图片文件直接预览图片效果")
    print("2. 在浏览器中打开HTML文件查看完整的MBTI风格展示")
    print("=" * 60)

if __name__ == "__main__":
    preview_all_result_images()
