# config/settings.py

# --- 文件路径 ---
HTS_DB_FILENAME = "../HTS_DB.xlsx"
EMAIL_TEMPLATE_FILENAME = "../EmailBlurb.xlsx"

# --- 邮件标签映射表 (HTS DB 列名 -> 邮件标签) ---
EMAIL_MAPPING = {
    "MF (Textile)": "Manufacturer(纺织品)",
    "Component": "Material compositions for textiles",
    "FDA Information+ DII+ Drop ball test": "Drop Ball Test and DII",
    "IFI": "IFI Form required",
    "Lacey Act (based on Implementation Schedule)": "Need Lacey Act (& TSCA)",
    "Aluminum Products": "Section 232 Aluminum",
    "Aluminum - derivative products": "Sec_232 钢铁铝铜及衍生品发票填写邮件模板, Section 232 Aluminum",
    "Steel Products": "钢铁熔炼国浇铸国",
    "Steel - derivative products": "Sec_232 钢铁铝铜及衍生品发票填写邮件模板, 钢铁熔炼国浇铸国",
    "Copper - derivative products": "Sec_232 钢铁铝铜及衍生品发票填写邮件模板"
}

# --- 自定义标签 (用于在 Excel 模板中指示样式) ---
TAG_RED_START = "<RED>"
TAG_RED_END = "</RED>"
TAG_BOLD_START = "<BOLD>"
TAG_BOLD_END = "</BOLD>"
TAG_REDBOLD_START = "<REDBOLD>"
TAG_REDBOLD_END = "</REDBOLD>"

# --- Word 文档常量 ---
GREETINGS = {
    'EN': "Hello Seller,",
    'CH': "尊敬的卖家，"
}
CLOSINGS = {
    'EN': "If you have any questions, please contact us in time. Thanks！",
    'CH': "如果您有任何问题，请及时联系我们。谢谢！"
}
SIGNATURE = "Your own signature"