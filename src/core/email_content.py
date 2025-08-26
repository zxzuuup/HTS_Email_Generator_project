# src/core/email_content.py
from config.settings import EMAIL_MAPPING


class EmailContentExtractor:
    @staticmethod
    def extract_and_merge_content(matched_columns, email_templates):
        """根据匹配列名提取并合并邮件内容（包含样式信息）"""
        all_labels = []

        for column in matched_columns:
            if column not in EMAIL_MAPPING:
                continue

            labels = [label.strip() for label in EMAIL_MAPPING[column].split(',')]
            all_labels.extend(labels)

        seen = set()
        unique_labels = []
        for label in all_labels:
            if label not in seen:
                seen.add(label)
                unique_labels.append(label)

        english_text_parts = []
        english_style_parts = []
        chinese_text_parts = []
        chinese_style_parts = []

        for label in unique_labels:
            if label in email_templates:
                data = email_templates[label]

                if data['english_text']:
                    english_text_parts.append(data['english_text'])
                    english_style_parts.append(data['english_styles'])

                if data['chinese_text']:
                    chinese_text_parts.append(data['chinese_text'])
                    chinese_style_parts.append(data['chinese_styles'])

        return english_text_parts, english_style_parts, chinese_text_parts, chinese_style_parts