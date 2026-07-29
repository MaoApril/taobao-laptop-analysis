"""
淘宝笔记本电脑市场数据可视化分析
=====================================
合并版本：将6张分析图整合到一个脚本中，一键运行生成全部可视化结果。
输出目录：../output/

确保以下文件存在：
  - data/cleaned_data.csv    # 清洗后的数据
  - data/stopwords.txt       # 停用词表（词云用）
  - data/computer.png        # 词云形状遮罩图
  - data/simhei.ttf          # 中文字体文件（词云用）
"""

import os
import numpy as np
import pandas as pd
import jieba
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from PIL import Image

# ===================== 全局配置 =====================

sns.set_theme(style='whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 以脚本位置为基准，定位项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取清洗后的数据
DATA_PATH = os.path.join(DATA_DIR, 'cleaned_data.csv')
df = pd.read_csv(DATA_PATH)

# ===================== 图1：不同价格区间的商品数量分布 =====================

def plot_price_distribution_count():
    """不同价格区间的商品数量分布——柱状图"""
    bins = [3000, 5000, 7000, 9000, 10000, 20000, np.inf]
    labels = ['3000-5000元', '5000-7000元', '7000-9000元',
              '9000-10000元', '10000-20000元', '20000元以上']

    df_tmp = df.copy()
    df_tmp['价格区间'] = pd.cut(df_tmp['价格'], bins=bins, labels=labels, right=False)
    counts = df_tmp['价格区间'].value_counts().reindex(labels, fill_value=0).reset_index()
    counts.columns = ['价格区间', '商品数量']

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=counts, x='价格区间', y='商品数量',
                     hue='价格区间', palette='Blues_r', legend=False)
    for i, v in enumerate(counts['商品数量']):
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

    plt.title('不同价格区间的商品数量分布')
    plt.xlabel('价格区间')
    plt.ylabel('商品数量')
    plt.xticks(rotation=30)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, 'price_distribution_count.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'[OK] 价格区间商品数量柱状图 → {path}')


# ===================== 图2：不同价格区间的销量分布 =====================

def plot_price_distribution_sales():
    """不同价格区间的销量分布——柱状图"""
    custom_bins = [3000, 5000, 7000, 9000, 10000, 20000, np.inf]
    custom_labels = ['3000-5000元', '5000-7000元', '7000-9000元',
                     '9000-10000元', '10000-20000元', '20000元以上']

    df_tmp = df.dropna(subset=['销量']).copy()
    df_tmp['价格区间'] = pd.cut(df_tmp['价格'], bins=custom_bins,
                               labels=custom_labels, right=False)

    sales_by_price = df_tmp.groupby('价格区间', observed=False)['销量'].sum() \
        .reindex(custom_labels, fill_value=0).reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=sales_by_price, x='价格区间', y='销量',
                     hue='价格区间', palette='YlOrRd_r', legend=False)
    for i, v in enumerate(sales_by_price['销量']):
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

    plt.title('不同价格区间的销量表现')
    plt.xlabel('价格区间')
    plt.ylabel('销量')
    plt.xticks(rotation=30)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, 'price_distribution_sales.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'[OK] 价格区间销量分布柱状图 → {path}')


# ===================== 图3：不同类型的销量分布 =====================

def classify_laptop_type(title):
    """根据商品标题关键词分类笔记本电脑类型"""
    if '轻薄' in title:
        return '轻薄本'
    if '游戏' in title:
        return '游戏本'
    if '二合一' in title:
        return '二合一笔记本'
    return '其他类型'


def plot_type_distribution_sales():
    """不同笔记本电脑类型的销量分布——环形饼图（3个品类适合饼图）"""
    df_tmp = df.copy()
    df_tmp['笔记本电脑类型'] = df_tmp['标题'].apply(classify_laptop_type)

    # 排除"其他类型"，只看三大主力品类
    sales = df_tmp[df_tmp['笔记本电脑类型'] != '其他类型'] \
        .groupby('笔记本电脑类型')['销量'].sum().reset_index()

    colors = sns.color_palette('Set2', len(sales))

    plt.figure(figsize=(8, 8))
    plt.pie(sales['销量'], labels=sales['笔记本电脑类型'],
            autopct='%1.1f%%', startangle=140, colors=colors,
            explode=[0.03] * len(sales),
            wedgeprops=dict(width=0.4, edgecolor='w'))

    plt.legend(sales['笔记本电脑类型'], loc='upper right', fontsize=10)
    plt.title('不同笔记本电脑类型的销量分布', pad=25, fontsize=18)
    plt.axis('equal')

    path = os.path.join(OUTPUT_DIR, 'type_distribution_sales.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'[OK] 类型销量分布饼图 → {path}')


# ===================== 图4：产地Top10柱状图 =====================

def plot_top10_origin():
    """笔记本电脑产地Top10（城市/省份）——柱状图"""
    df_tmp = df.copy()

    # 将未知城市替换为省份，处理空值
    df_tmp['城市'] = df_tmp['城市'].replace({'未知': np.nan, '': np.nan}).fillna(df_tmp['省份'])

    cities_top10 = df_tmp.groupby('城市')['销量'].sum().nlargest(10).reset_index()

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=cities_top10, x='城市', y='销量',
                     hue='城市', palette='tab20', legend=False)
    for i, v in enumerate(cities_top10['销量']):
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

    plt.title('笔记本电脑产地Top10（城市/省份）')
    plt.xlabel('地区')
    plt.ylabel('销量')
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, 'top10_origin.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'[OK] 产地Top10柱状图 → {path}')


# ===================== 图5：商品标题词云图 =====================

def plot_wordcloud():
    """商品标题词云图"""
    # 加载标题列
    titles = df['标题'].dropna()

    # 加载停用词
    stopwords_path = os.path.join(DATA_DIR, 'stopwords.txt')
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().splitlines())

    # 对所有标题进行分词并合并
    combined_text = ' '.join(
        ' '.join(word for word in jieba.cut(title) if word not in stopwords)
        for title in titles
    )

    # 加载词云形状遮罩
    try:
        mask = np.array(Image.open(os.path.join(DATA_DIR, 'computer.png')))
    except FileNotFoundError:
        print('[WARN] 未找到词云遮罩图 data/computer.png，将使用矩形画布')
        mask = None

    # 生成词云
    font_path = os.path.join(DATA_DIR, 'simhei.ttf')
    wordcloud_kwargs = dict(
        font_path=font_path,
        background_color='white',
        contour_width=2,
        contour_color='steelblue',
        width=800, height=600,
        max_words=200,
        max_font_size=150,
        min_font_size=15,
        prefer_horizontal=1,
    )
    if mask is not None:
        wordcloud_kwargs['mask'] = mask

    wordcloud = WordCloud(**wordcloud_kwargs).generate(combined_text)

    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    path = os.path.join(OUTPUT_DIR, 'wordcloud_title.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'[OK] 商品标题词云图 → {path}')


# ===================== 图6：销量Top15品牌柱状图 =====================

# 品牌识别关键词字典
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
    """根据标题关键词提取品牌名"""
    for brand, keywords in BRANDS_DICT.items():
        if any(kw in title for kw in keywords):
            return brand
    return '未知品牌'


def plot_top15_brands():
    """笔记本电脑销量Top15品牌——柱状图"""
    df_tmp = df.copy()
    df_tmp['品牌'] = df_tmp['标题'].apply(extract_brand)
    df_tmp = df_tmp[df_tmp['品牌'] != '未知品牌']

    sales = df_tmp.groupby('品牌')['销量'].sum().nlargest(15).reset_index()

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=sales, x='品牌', y='销量',
                     hue='品牌', palette='viridis_r', legend=False)
    for i, v in enumerate(sales['销量']):
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

    plt.title('笔记本电脑销量Top15品牌')
    plt.xlabel('品牌')
    plt.ylabel('销量')
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, 'top15_brand_sales.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'[OK] 销量Top15品牌柱状图 → {path}')


# ===================== 主入口 =====================

if __name__ == '__main__':
    print('=' * 60)
    print('  淘宝笔记本电脑市场数据可视化分析')
    print('=' * 60)
    print(f'  数据文件: {DATA_PATH}')
    print(f'  数据量: {len(df)} 条')
    print(f'  输出目录: {os.path.abspath(OUTPUT_DIR)}')
    print('=' * 60)

    plot_price_distribution_count()
    plot_price_distribution_sales()
    plot_type_distribution_sales()
    plot_top10_origin()
    plot_wordcloud()
    plot_top15_brands()

    print('=' * 60)
    print('  全部 6 张图表生成完毕！')
    print('=' * 60)
