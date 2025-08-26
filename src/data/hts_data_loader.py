# src/data/hts_data_loader.py
import pandas as pd
import os

class HTSDataLoader:
    @staticmethod
    def load_hts_database(file_path):
        """加载 HTS 数据库"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HTS 数据库文件不存在: {file_path}")
        try:
            df = pd.read_excel(file_path, header=0, engine='openpyxl')
            return df
        except Exception as e:
            raise Exception(f"读取 HTS 数据库失败: {e}")