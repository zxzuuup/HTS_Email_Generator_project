# src/data/email_template_loader.py
import pandas as pd
import os
from ..utils.helpers import parse_blurb_with_tags
from config.settings import TAG_RED_START, TAG_RED_END, TAG_BOLD_START, TAG_BOLD_END, TAG_REDBOLD_START, TAG_REDBOLD_END


class EmailTemplateLoader:
    @staticmethod
    def load_email_templates(file_path):
        """加载邮件模板文件，支持样式标签"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"邮件模板文件不存在: {file_path}")

        try:
            df = pd.read_excel(file_path, sheet_name=0, usecols="A:C", header=0)
            df = df.dropna(subset=['Issue Details Description'])
        except Exception as e:
            raise Exception(f"读取邮件模板文件失败: {e}")

        email_dict = {}
        for _, row in df.iterrows():
            label = str(row['Issue Details Description']).strip()

            raw_english = str(row.get('English Email Blurb', '')).strip().rstrip('\n')
            raw_chinese = str(row.get('Chinese Email Blurb', '')).strip().rstrip('\n')

            en_text, en_styles = parse_blurb_with_tags(raw_english, TAG_RED_START, TAG_RED_END, TAG_BOLD_START,
                                                       TAG_BOLD_END, TAG_REDBOLD_START, TAG_REDBOLD_END)
            ch_text, ch_styles = parse_blurb_with_tags(raw_chinese, TAG_RED_START, TAG_RED_END, TAG_BOLD_START,
                                                       TAG_BOLD_END, TAG_REDBOLD_START, TAG_REDBOLD_END)

            email_dict[label] = {
                'english_text': en_text,
                'english_styles': en_styles,
                'chinese_text': ch_text,
                'chinese_styles': ch_styles
            }

        return email_dict