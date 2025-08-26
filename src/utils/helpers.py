# src/utils/helpers.py
import sys
import os


def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和 PyInstaller 环境"""
    try:
        # PyInstaller 创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def parse_blurb_with_tags(raw_blurb, tag_red_start, tag_red_end, tag_bold_start, tag_bold_end, tag_redbold_start,
                          tag_redbold_end):
    """解析带有自定义标签的邮件内容，返回 (纯文本, 样式信息列表)"""
    import re
    if not raw_blurb:
        return "", []

    parsed_parts = []
    styles = []

    pattern = re.compile(
        rf'({re.escape(tag_red_start)}|{re.escape(tag_bold_start)}|{re.escape(tag_redbold_start)})'
        rf'(.*?)'
        rf'({re.escape(tag_red_end)}|{re.escape(tag_bold_end)}|{re.escape(tag_redbold_end)})',
        re.DOTALL
    )

    last_end = 0
    for match in pattern.finditer(raw_blurb):
        prefix = raw_blurb[last_end:match.start()]
        if prefix:
            parsed_parts.append(prefix)
            styles.append('normal')

        start_tag = match.group(1)
        content = match.group(2)
        end_tag = match.group(3)

        if start_tag == tag_red_start and end_tag == tag_red_end:
            style = 'red'
        elif start_tag == tag_bold_start and end_tag == tag_bold_end:
            style = 'bold'
        elif start_tag == tag_redbold_start and end_tag == tag_redbold_end:
            style = 'redbold'
        else:
            parsed_parts.append(match.group(0))
            styles.append('normal')
            last_end = match.end()
            continue

        parsed_parts.append(content)
        styles.append(style)
        last_end = match.end()

    suffix = raw_blurb[last_end:]
    if suffix:
        parsed_parts.append(suffix)
        styles.append('normal')

    return "".join(parsed_parts), list(zip(parsed_parts, styles))