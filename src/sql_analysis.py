"""
淘宝笔记本电脑数据 → SQLite 数据库构建
======================================
将清洗后的 CSV 导入 SQLite，并添加价格区间、品牌、笔记本类型三个衍生列，
为 src/sql_analysis.sql 中的查询提供数据基础。

运行方式：
    python src/sql_analysis.py

输出文件：
    data/taobao.db
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CSV_PATH = os.path.join(DATA_DIR, 'cleaned_data.csv')
DB_PATH = os.path.join(DATA_DIR, 'taobao.db')

# ===================== 品牌识别字典（与 visualization.py 保持一致）=====================

BRANDS_DICT = {
    '联想': ['联想', '小新', 'Lenovo', 'lenovo', 'ThinkPad', 'Thinkpad', 'thinkpad'],
    '惠普': ['惠普', 'HP'],
    '华硕': ['华硕', 'Asus', 'ASUS', 'asus'],
    '华为': ['华为', 'HUAWEI', 'Huawei', 'huawei'],
    '苹果': ['苹果', 'Apple', 'apple'],
    '戴尔': ['戴尔', 'Dell', 'DELL', 'dell'],
    '小米': ['小米', 'Xiaomi', 'xiaomi'],
    '机械革命': ['机械', '革命', 'MECHREVO'],
    '宏碁': ['宏碁', 'Acer', 'acer'],
    '荣耀': ['荣耀', 'honor', 'HONOR', 'Honor'],
    '外星人': ['外星人', 'Alienware', 'alienware', 'ALIENWARE', 'AlienWare'],
    '雷神': ['雷神'],
    '玩家国度': ['玩家', '国度', 'ROG', 'rog'],
    '神舟': ['神舟', '神州', 'Hasee', 'HASEE'],
    '微软': ['Microsoft', '微软'],
}


def extract_brand(title):
    for brand, keywords in BRANDS_DICT.items():
        if isinstance(title, str) and any(kw in title for kw in keywords):
            return brand
    return '未知品牌'


def classify_type(title):
    if not isinstance(title, str):
        return '其他类型'
    if '轻薄' in title:
        return '轻薄本'
    if '游戏' in title:
        return '游戏本'
    if '二合一' in title:
        return '二合一笔记本'
    return '其他类型'


def classify_price(price):
    if pd.isna(price):
        return '未知'
    if price < 3000:
        return '3000元以下'
    if price < 5000:
        return '3000-5000元'
    if price < 7000:
        return '5000-7000元'
    if price < 9000:
        return '7000-9000元'
    if price < 10000:
        return '9000-10000元'
    if price < 20000:
        return '10000-20000元'
    return '20000元以上'


def main():
    print('=' * 60)
    print('  淘宝笔记本电脑数据 → SQLite 数据库构建')
    print('=' * 60)

    # 读取 CSV
    df = pd.read_csv(CSV_PATH)
    print(f'  读取数据: {CSV_PATH}')
    print(f'  原始行数: {len(df)} 条')
    print(f'  原始列名: {list(df.columns)}')

    # 添加衍生列
    df['品牌'] = df['标题'].apply(extract_brand)
    df['笔记本类型'] = df['标题'].apply(classify_type)
    df['价格区间'] = df['价格'].apply(classify_price)

    print(f'  衍生列:   品牌 / 笔记本类型 / 价格区间')
    print(f'  品牌分布: {df["品牌"].value_counts().to_dict()}')
    print(f'  类型分布: {df["笔记本类型"].value_counts().to_dict()}')
    print(f'  价格分布: {df["价格区间"].value_counts().to_dict()}')

    # 写入 SQLite
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('laptops', conn, if_exists='replace', index=False)
    conn.close()

    print(f'  数据库已生成: {DB_PATH}')
    print(f'  表名: laptops')
    print(f'  列名: {list(df.columns)}')
    print('=' * 60)
    print('  完成！可运行 sql_analysis.sql 中的查询进行验证。')
    print('=' * 60)


if __name__ == '__main__':
    main()
