import os
import re
import opencc

cc = opencc.OpenCC('s2twp.json')

SOURCE_DIR = "docs/guide/zh-cn"
TARGET_DIR = "docs/guide/zh-hant"

files = [
    "README.md",
    "01-basic-operations.md",
    "02-advanced-custom-recipes.md",
    "03-under-the-hood-and-internals.md",
    "04-faq-and-troubleshooting.md"
]

CUSTOM_TERMS = [
    ("軟連結", "符號連結 (Symlink)"),
    ("軟體連結", "符號連結 (Symlink)"),
    ("鑰匙串", "鑰匙圈"),
    ("程序塢", "Dock (程式塢)"),
    ("啟動台", "啟動台 (Launchpad)"),
    ("聚焦搜尋", "Spotlight 搜尋"),
    ("硬分身", "硬分身 (Hard Clone)"),
    ("軟分身", "軟分身 (Soft Clone)"),
    ("智能探針", "智慧探針 (App Prober)"),
    ("簡體中文版", "繁體中文版"),
    ("用戶手冊", "使用者手冊"),
    ("使用者使用手冊", "使用者手冊"),
    ("用戶使用手冊", "使用者手冊"),
    ("官方使用手冊", "官方使用手冊"),
    ("普通用戶", "一般使用者"),
    ("小白用戶", "初學者 / 一般使用者"),
    ("極客玩家", "極客玩家 / 開發者"),
]

def convert_text(content):
    code_blocks = []
    def save_fenced(m):
        code_blocks.append(m.group(0))
        return f"__FENCED_CODE_BLOCK_{len(code_blocks)-1}__"
    content = re.sub(r'```[\s\S]*?```', save_fenced, content)
    
    inline_codes = []
    def save_inline(m):
        inline_codes.append(m.group(0))
        return f"__INLINE_CODE_{len(inline_codes)-1}__"
    content = re.sub(r'`[^`\n]+`', save_inline, content)

    html_tags = []
    def save_html(m):
        html_tags.append(m.group(0))
        return f"__HTML_TAG_{len(html_tags)-1}__"
    content = re.sub(r'<[^>]+>', save_html, content)

    converted = cc.convert(content)

    for src, dst in CUSTOM_TERMS:
        converted = converted.replace(src, dst)

    for i, tag in enumerate(html_tags):
        converted = converted.replace(f"__HTML_TAG_{i}__", tag)

    for i, code in enumerate(inline_codes):
        converted = converted.replace(f"__INLINE_CODE_{i}__", code)

    for i, block in enumerate(code_blocks):
        converted = converted.replace(f"__FENCED_CODE_BLOCK_{i}__", block)

    return converted

os.makedirs(TARGET_DIR, exist_ok=True)

for filename in files:
    src_path = os.path.join(SOURCE_DIR, filename)
    dst_path = os.path.join(TARGET_DIR, filename)
    with open(src_path, 'r', encoding='utf-8') as f:
        src_content = f.read()

    converted = convert_text(src_content)
    converted = re.sub(r'\[English Version \(英文版\)\]\(\.\./en/\)\s*\|\s*简体中文版', '[English Version](../en/) | [簡體中文](../zh/) | 繁體中文', converted)
    converted = re.sub(r'# 📖 ATBClone 用户使用手册（简体中文版）', '# 📖 ATBClone 使用者手冊（繁體中文版）', converted)

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(converted)
    print(f"✓ Converted {dst_path}")
