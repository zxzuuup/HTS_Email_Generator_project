# src/core/matcher.py
import pandas as pd


class HTSMatcher:
    @staticmethod
    def find_matching_columns(input_code, df):
        """根据输入的编码和 DataFrame，找出匹配的列标题"""
        matching_columns = []
        for column_name in df.columns:
            column_data = df[column_name]
            valid_codes = (
                column_data
                .fillna('')
                .astype(str)
                .str.strip()
                .str.replace(r'\s+', '', regex=True)
                .str.replace(r'\.0*$', '', regex=True)
                .str.replace(r'[eE][-+]?[0-9]+', '', regex=True)
                .loc[lambda x: x != '']
                .loc[lambda x: x.str.contains(r'^\d+$')]
            )

            matched = False
            for code in valid_codes:
                if len(code) <= len(input_code) and input_code.startswith(code):
                    matched = True
                    break

            if matched:
                matching_columns.append(column_name)

        return matching_columns
