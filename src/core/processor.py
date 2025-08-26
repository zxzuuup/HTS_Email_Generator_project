# src/core/processor.py
from .matcher import HTSMatcher
from .email_content import EmailContentExtractor
from .formatter import WordFormatter
from config.settings import GREETINGS, CLOSINGS, SIGNATURE


class HTSProcessor:
    """协调核心逻辑的高级别类"""

    def __init__(self, hts_data, email_templates):
        self.hts_data = hts_data
        self.email_templates = email_templates
        self.matcher = HTSMatcher()
        self.extractor = EmailContentExtractor()
        self.formatter = WordFormatter("HTS_Email.docx")

    def process_multi_code(self, codes, logger_func=print):
        results = []
        for code in codes:
            self.formatter.add_paragraph(f"编码:{code} 模板如下：", before_black=1, after_black=1)
            result = self.process_single_code(code, logger_func)
            results.append(result)
        self.formatter.save()
        return results

    def process_single_code(self, code, logger_func=print):
        """处理单个HTS编码的完整流程，返回生成的邮件内容"""
        logger_func(f"\n============================= 处理编码: {code} ==================================\n")

        matched_columns = self.matcher.find_matching_columns(code, self.hts_data)
        result = {
            'code': code,
            'matched_columns': matched_columns,
            'en_content': None,
            'ch_content': None
        }

        if not matched_columns:
            logger_func("❌ 无匹配列\n")
            return result

        for i, column in enumerate(matched_columns, 1):
            logger_func(f"{i}. {column}\n")

        logger_func("\n")

        en_text_parts, en_style_parts, ch_text_parts, ch_style_parts = self.extractor.extract_and_merge_content(
            matched_columns, self.email_templates)

        if not en_text_parts and not ch_text_parts:
            logger_func("❌ 未找到对应的邮件内容\n")
            return result

        # 生成格式化的文本内容（用于界面显示）
        en_full_content = self._format_for_display(en_text_parts, 'EN')
        ch_full_content = self._format_for_display(ch_text_parts, 'CH')

        result['en_content'] = en_full_content
        result['ch_content'] = ch_full_content

        if en_text_parts:
            try:
                self.formatter.format_and_save_word(en_text_parts, en_style_parts, code, 'EN')
                logger_func("✅ 英文邮件内容已生成\n")
            except Exception as e:
                logger_func(f"❌ 生成英文Word文件失败: {e}\n")

        self.formatter.add_paragraph(after_black=1)

        if ch_text_parts:
            try:
                self.formatter.format_and_save_word(ch_text_parts, ch_style_parts, code, 'CH')
                logger_func("✅ 中文邮件内容已生成\n")
            except Exception as e:
                logger_func(f"❌ 生成中文Word文件失败: {e}\n")

        logger_func(f"============================= 处理完成: {code} ==================================\n\n")
        return result

    def _format_for_display(self, text_parts, language):
        """格式化内容用于界面显示"""
        greeting = GREETINGS.get(language, "Hello Seller,")
        closing = CLOSINGS.get(language, "If you have any questions, please contact us in time. Thanks！")

        content = [greeting, ""]
        for i, part in enumerate(text_parts, 1):
            content.append(f"Question {i}:" if language == 'EN' else f"问题 {i}:")
            content.append(part)
            content.append("")

        content.append(closing)
        content.append(SIGNATURE)
        return "\n".join(content)