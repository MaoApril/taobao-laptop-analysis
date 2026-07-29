# 淘宝笔记本电脑市场数据采集与可视化分析

> 一个完整的"数据采集 → 数据清洗 → 探索性分析 → 可视化 → 业务建议"端到端数据分析项目。

## 项目背景

淘宝平台笔记本电脑 SKU 繁杂、价格段分散，消费者决策路径长。本项目通过采集平台在售商品数据，从价格带、品牌格局、产地分布、用户关注点等维度进行市场扫描，为品牌方与运营侧提供数据支持。

## 数据集

| 文件 | 说明 | 样本量 |
|---|---|---|
| `data/raw_data.csv` | 原始采集数据 | 4800 条 |
| `data/cleaned_data.csv` | 清洗后有效数据 | 3381 条 |

## 技术栈

- **数据采集**：Python Requests + BeautifulSoup
- **数据处理**：Pandas, NumPy
- **可视化**：Matplotlib, Seaborn
- **交互看板**：Power BI
- **文本分析**：jieba 分词 + WordCloud 词云

## 主要发现

- 联想品牌市场占有率达 **35%**
- **3000-5000 元**价格带贡献约 **60%** 销量
- 提炼出影响消费者决策的 **3 大核心因子**：品牌力、价格敏感度、配置梯度

## 项目结构

```
├── data/           # 数据集
├── src/            # Python 源码
├── output/         # 可视化图表
├── powerbi/        # Power BI 交互看板
├── notebooks/      # 分析 notebook
└── report/         # 项目报告
```

## 可视化成果

| 图表 | 说明 |
|---|---|
| 价格区间商品数量分布 | 了解市场供应结构 |
| 价格区间销量分布 | 识别主力消费价格带 |
| 商品类型销量分布 | 洞察品类偏好 |
| 产地 Top10 | 区域竞争格局 |
| 销量 Top15 品牌 | 头部品牌集中度 |
| 商品标题词云 | 消费者关注热点 |

## 如何运行

```bash
git clone https://github.com/MaoApril/taobao-laptop-analysis.git
cd taobao-laptop-analysis
pip install -r requirements.txt
python src/visualization.py
```

## 报告与看板

- 完整分析报告见 `report/taobao_laptop_analysis_report.pdf`
- Power BI 交互看板见 `powerbi/taobao_laptop_dashboard.pbix`（制作中）

## 联系方式

- **姓名**：冒婷婷
- **邮箱**：3486250452@qq.com
- **求职方向**：数据分析师（Base 深圳）
