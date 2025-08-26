# src/core/processor.py
# (这个文件可以整合 matcher, email_content, formatter 的调用逻辑，
#  但为了保持职责单一，我们可以让 GUI 或 main.py 来协调调用。
#  这里可以放一个更高级别的协调函数，如果需要的话。)
# 例如：
from .matcher import HTSMatcher
from .email_content import EmailContentExtractor
from .formatter import WordFormatter


class HTSProcessor:
    """协调核心逻辑的高级别类"""

    def __init__(self, hts_data, email_templates):
        self.hts_data = hts_data
        self.email_templates = email_templates
        self.matcher = HTSMatcher()
        self.extractor = EmailContentExtractor()
        self.formatter = WordFormatter("HTS_Email.docx")

    def process_multi_code(self, codes, logger_func=print):
        for code in codes:
            self.formatter.add_paragraph("编码:{} 模板如下：".format(code), before_black=1, after_black=1)
            self.process_single_code(code, logger_func)
        self.formatter.save()

    def process_single_code(self, code, logger_func=print):
        """处理单个HTS编码的完整流程"""
        logger_func(f"\n============================= 处理编码: {code} ==================================\n")

        matched_columns = self.matcher.find_matching_columns(code, self.hts_data)

        if not matched_columns:
            logger_func("❌ 无匹配列\n")
            return []

        for i, column in enumerate(matched_columns, 1):
            logger_func(f"{i}. {column}\n")

        logger_func("\n")

        en_text_parts, en_style_parts, ch_text_parts, ch_style_parts = self.extractor.extract_and_merge_content(
            matched_columns, self.email_templates)

        if not en_text_parts and not ch_text_parts:
            logger_func("❌ 未找到对应的邮件内容\n")

        if en_text_parts:
            try:
                self.formatter.format_and_save_word(en_text_parts, en_style_parts, code, 'EN')
            except Exception as e:
                logger_func(f"❌ 生成 Word 文件失败: {e}\n")

        self.formatter.add_paragraph(after_black=1)

        if ch_text_parts:
            try:
                self.formatter.format_and_save_word(ch_text_parts, ch_style_parts, code, 'CH')
            except Exception as e:
                logger_func(f"❌ 生成 Word 文件失败: {e}\n")

        logger_func(f"============================= 处理完成: {code} ==================================\n\n")