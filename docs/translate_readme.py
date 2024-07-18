from googletrans import Translator
import json
import os
import re
import time

# 创建翻译器实例
translator = Translator()

# 读取 JSON 文件中的翻译列表
with open('docs/translate_readme.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 正则表达式匹配中文字符
chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')

# 遍历 translatelist 中的每个条目
for item in data['translatelist']:
    if not item.get('translated', False):  # 检查 translated 的值，如果为 False 则跳过
        print(f"条目 {item['foldpath']} 的 translated 为 false，跳过翻译。")
        continue

    foldpath = item['foldpath']
    translatefile = item['translatefile']
    translatedto = item['translatedto']

    # 读取要翻译的 README 文件
    readme_path = os.path.join(foldpath, translatefile)
    if not os.path.exists(readme_path):
        print(f'文件 {readme_path} 不存在，跳过翻译。')
        continue

    with open(readme_path, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()

    # 提取中文文本进行翻译
    for lang in translatedto:
        # 创建目标文件的路径
        output_path = os.path.join(foldpath, f'README_{lang}.md')

        # 存储中文文本的位置和对应的翻译
        translations = []

        for line_number, line in enumerate(lines):
            # 查找所有中文文本
            for match in chinese_pattern.finditer(line):
                chinese_text = match.group()
                # 翻译中文文本
                try:
                    translated_text = translator.translate(chinese_text, src='zh-CN', dest=lang).text
                except Exception as e:
                    print(f"翻译错误：{e}")
                    translated_text = chinese_text  # 发生错误时使用原文本
                # 记录中文文本的位置和翻译
                translations.append((line_number, chinese_text, translated_text))
               # time.sleep(0.5)  # 添加请求间隔时间以防止被限制

        # 替换文本中的中文部分为翻译后的文本
        new_lines = []
        for line_number, line in enumerate(lines):
            # 将翻译后的中文文本替换为目标语言的翻译
            for original_text, translated_text in [(text, trans) for ln, text, trans in translations if ln == line_number]:
                line = line.replace(original_text, translated_text)
            new_lines.append(line)  # 添加翻译后的行内容

        # 新建或覆盖目标文件并保存翻译后的内容
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.writelines(new_lines)

        print(f"翻译完成，已将 {lang} 语言的结果写入 '{output_path}'。")
