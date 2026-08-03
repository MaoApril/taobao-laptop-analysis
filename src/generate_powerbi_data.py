"""
生成 Power BI 专用数据文件
============================
1. powerbi_data.csv  — 带衍生列（价格区间/品牌/类型）的增强数据
2. word_freq.csv     — 标题分词词频表（Power BI 词云用）
"""

import os
import pandas as pd
import jieba

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# ============ 读取原始数据 ============
df = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_data.csv'))
print(f'读取数据: {len(df)} 条')

# ============ 1. 价格区间 ============
bins = [0, 3000, 5000, 7000, 9000, 10000, 20000, float('inf')]
labels = ['3000元以下', '3000-5000元', '5000-7000元',
          '7000-9000元', '9000-10000元', '10000-20000元', '20000元以上']
df['价格区间'] = pd.cut(df['价格'], bins=bins, labels=labels, right=False)

# ============ 2. 品牌提取 ============
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
    if not isinstance(title, str):
        return '其他品牌'
    for brand, keywords in BRANDS_DICT.items():
        if any(kw in title for kw in keywords):
            return brand
    return '其他品牌'

df['品牌'] = df['标题'].apply(extract_brand)

# ============ 3. 笔记本类型 ============
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

df['笔记本类型'] = df['标题'].apply(classify_type)

# ============ 4. 保存增强数据 ============
df_out = df[['标题', '价格', '价格区间', '品牌', '笔记本类型',
             '省份', '城市', '销量', '店铺']].copy()
df_out.to_csv(os.path.join(DATA_DIR, 'powerbi_data.csv'),
              index=False, encoding='utf-8-sig')
print(f'[OK] powerbi_data.csv 已生成 ({len(df_out)} 行)')

# ============ 5. 词频统计（词云用）============
stopwords_path = os.path.join(DATA_DIR, 'stopwords.txt')
with open(stopwords_path, 'r', encoding='utf-8') as f:
    stopwords = set(f.read().splitlines())

# 额外过滤无意义词
extra_stop = {'笔记本', '电脑', '笔记本电脑', '的', '了', '和', '与', '在',
              '14', '15', '16', '13', '英寸', 'i5', 'i7', 'i9',
              '16G', '32G', '8G', '512G', '1T', 'SSD',
              'nbsp', 'amp', 'quot', 'gt', 'lt'}
stopwords.update(extra_stop)

words = []
for title in df['标题'].dropna():
    for word in jieba.cut(title):
        word = word.strip()
        if len(word) >= 2 and word not in stopwords and not word.isdigit():
            words.append(word)

word_freq = pd.Series(words).value_counts().reset_index()
word_freq.columns = ['词语', '频次']
word_freq = word_freq.head(150)  # 取前150高频词
word_freq.to_csv(os.path.join(DATA_DIR, 'word_freq.csv'),
                 index=False, encoding='utf-8-sig')
print(f'[OK] word_freq.csv 已生成 ({len(word_freq)} 个词)')

# 打印预览
print('\n=== 价格区间分布 ===')
print(df_out['价格区间'].value_counts().sort_index())
print('\n=== 品牌分布 (Top10) ===')
print(df_out['品牌'].value_counts().head(10))
print('\n=== 类型分布 ===')
print(df_out['笔记本类型'].value_counts())
print('\n=== 词频 Top15 ===')
print(word_freq.head(15).to_string(index=False))
