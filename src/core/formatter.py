# src/core/formatter.py
from docx import Document
from docx.shared import RGBColor
from config.settings import GREETINGS, CLOSINGS, SIGNATURE


class WordFormatter:

    @staticmethod
    def _apply_word_style(run, style):
        """为 python-docx 的 run 应用样式"""
        if style == 'red':
            run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)  # 红色
        elif style == 'bold':
            run.bold = True
        elif style == 'redbold':
            run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)  # 红色
            run.bold = True
        # normal 样式无需特殊处理

    @staticmethod
    def format_and_save_word(text_parts, style_parts, code, language):
        """格式化内容并保存为 Word 文档"""
        word_doc = Document()

        greeting = GREETINGS.get(language, "Hello Seller,")
        closing = CLOSINGS.get(language, "If you have any questions, please contact us in time. Thanks！")

        word_doc.add_paragraph(greeting)
        word_doc.add_paragraph()

        for i, (text, styles) in enumerate(zip(text_parts, style_parts)):
            if i > 0:
                word_doc.add_paragraph()

            question_title = f"Question {i + 1}:" if language == 'EN' else f"问题 {i + 1}:"
            title_para = word_doc.add_paragraph()
            title_para.add_run(question_title)

            content_para = word_doc.add_paragraph()
            full_text = text

            if not styles:
                content_para.add_run(full_text)
            else:
                last_end_idx = 0
                for part_text, part_style in styles:
                    start_idx = full_text.find(part_text, last_end_idx)
                    if start_idx == -1:
                        run = content_para.add_run(part_text)
                        WordFormatter._apply_word_style(run, 'normal')
                        continue

                    if start_idx > last_end_idx:
                        prefix = full_text[last_end_idx:start_idx]
                        run = content_para.add_run(prefix)
                        WordFormatter._apply_word_style(run, 'normal')

                    styled_run = content_para.add_run(part_text)
                    WordFormatter._apply_word_style(styled_run, part_style)

                    last_end_idx = start_idx + len(part_text)

                if last_end_idx < len(full_text):
                    suffix = full_text[last_end_idx:]
                    run = content_para.add_run(suffix)
                    WordFormatter._apply_word_style(run, 'normal')

        word_doc.add_paragraph()
        word_doc.add_paragraph(closing)
        word_doc.add_paragraph()
        word_doc.add_paragraph(SIGNATURE)

        filename = f"HTS_Email_{code}_{language}.docx"
        word_doc.save(filename)
        return filename