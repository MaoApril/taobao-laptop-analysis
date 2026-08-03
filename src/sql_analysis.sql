-- ============================================================
-- 淘宝笔记本电脑市场分析 — SQL 复刻查询
-- ============================================================
-- 数据库：SQLite  (data/taobao.db)
-- 表名：  laptops
-- 列：    标题, 价格, 省份, 城市, 销量, 店铺, 品牌, 笔记本类型, 价格区间
--
-- 使用方法：
--   1. 先运行 python src/sql_analysis.py 生成 taobao.db
--   2. 用 DB Browser for SQLite 打开 data/taobao.db
--   3. 逐条粘贴执行以下查询
-- ============================================================


-- ============================================================
-- 查询 1：各品牌销量排名（窗口函数 RANK）
-- 知识点：GROUP BY + 聚合 + 窗口函数排名
-- ============================================================
SELECT
    品牌,
    SUM(销量) AS 总销量,
    RANK() OVER (ORDER BY SUM(销量) DESC) AS 销量排名,
    ROUND(SUM(销量) * 100.0 / (SELECT SUM(销量) FROM laptops WHERE 品牌 != '未知品牌'), 2) AS 市场份额百分比
FROM laptops
WHERE 品牌 != '未知品牌'
GROUP BY 品牌
ORDER BY 总销量 DESC;


-- ============================================================
-- 查询 2：各价格区间的商品数量与总销量（CTE + CASE WHEN 分组）
-- 知识点：CTE + CASE WHEN 条件分类 + 聚合
-- ============================================================
WITH priced AS (
    SELECT
        *,
        CASE
            WHEN 价格 < 3000 THEN '1_3000元以下'
            WHEN 价格 < 5000 THEN '2_3000-5000元'
            WHEN 价格 < 7000 THEN '3_5000-7000元'
            WHEN 价格 < 9000 THEN '4_7000-9000元'
            WHEN 价格 < 10000 THEN '5_9000-10000元'
            WHEN 价格 < 20000 THEN '6_10000-20000元'
            ELSE '7_20000元以上'
        END AS 价格带
    FROM laptops
)
SELECT
    价格带,
    COUNT(*) AS 商品数量,
    SUM(销量) AS 总销量,
    ROUND(AVG(价格), 0) AS 平均价格
FROM priced
GROUP BY 价格带
ORDER BY 价格带;


-- ============================================================
-- 查询 3：各品牌累计销量占比（窗口函数 SUM OVER）
-- 知识点：窗口函数累计求和 + 市场集中度分析
-- ============================================================
WITH brand_sales AS (
    SELECT
        品牌,
        SUM(销量) AS 总销量
    FROM laptops
    WHERE 品牌 != '未知品牌'
    GROUP BY 品牌
)
SELECT
    品牌,
    总销量,
    SUM(总销量) OVER (ORDER BY 总销量 DESC) AS 累计销量,
    ROUND(
        SUM(总销量) OVER (ORDER BY 总销量 DESC) * 100.0
        / SUM(总销量) OVER (),
        2
    ) AS 累计市场份额百分比
FROM brand_sales
ORDER BY 总销量 DESC;


-- ============================================================
-- 查询 4：各品牌销量 Top3 爆款商品（窗口函数 ROW_NUMBER + PARTITION BY）
-- 知识点：分组内排名，找出每个品牌的明星产品
-- ============================================================
WITH ranked AS (
    SELECT
        品牌,
        标题,
        价格,
        销量,
        ROW_NUMBER() OVER (PARTITION BY 品牌 ORDER BY 销量 DESC) AS 组内排名
    FROM laptops
    WHERE 品牌 != '未知品牌'
)
SELECT
    品牌,
    标题,
    价格,
    销量,
    组内排名
FROM ranked
WHERE 组内排名 <= 3
ORDER BY 品牌, 组内排名;


-- ============================================================
-- 查询 5：各产地平均价格与商品数（聚合 + HAVING 过滤）
-- 知识点：GROUP BY + HAVING + 子查询过滤异常值
-- ============================================================
SELECT
    城市 AS 产地,
    ROUND(AVG(价格), 0) AS 平均价格,
    COUNT(*) AS 商品数量,
    SUM(销量) AS 总销量
FROM laptops
WHERE 城市 != '未知'
  AND 城市 IS NOT NULL
  AND 城市 != ''
GROUP BY 城市
HAVING COUNT(*) > 10
ORDER BY 平均价格 DESC;


-- ============================================================
-- 查询 6：价格高于全市场均价的商品占比（子查询 + CASE WHEN 统计）
-- 知识点：标量子查询 + 条件计数
-- ============================================================
SELECT
    COUNT(*) AS 总商品数,
    COUNT(CASE WHEN 价格 > (SELECT AVG(价格) FROM laptops) THEN 1 END) AS 高于均价数,
    ROUND(
        COUNT(CASE WHEN 价格 > (SELECT AVG(价格) FROM laptops) THEN 1 END) * 100.0
        / COUNT(*),
        2
    ) AS 高于均价百分比,
    ROUND((SELECT AVG(价格) FROM laptops), 0) AS 全市场均价
FROM laptops;


-- ============================================================
-- 查询 7：爆款商品分析 — 销量分层统计（CASE WHEN 分桶 + 多指标）
-- 知识点：CASE WHEN 分层 + 聚合 + 多维度交叉
-- ============================================================
SELECT
    CASE
        WHEN 销量 = 0 THEN '0_零销量'
        WHEN 销量 < 100 THEN '1_低销量(<100)'
        WHEN 销量 < 1000 THEN '2_中销量(100-1000)'
        WHEN 销量 < 5000 THEN '3_高销量(1000-5000)'
        ELSE '4_爆款(5000+)'
    END AS 销量分层,
    COUNT(*) AS 商品数量,
    ROUND(AVG(价格), 0) AS 平均价格,
    SUM(销量) AS 分层总销量,
    ROUND(SUM(销量) * 100.0 / (SELECT SUM(销量) FROM laptops), 2) AS 销量贡献百分比
FROM laptops
GROUP BY 销量分层
ORDER BY 销量分层;


-- ============================================================
-- 查询 8：Top5 品牌的价格区间交叉分布（多层 CTE + INNER JOIN）
-- 知识点：CTE 嵌套 + JOIN + 交叉分析
-- ============================================================
WITH brand_total AS (
    SELECT 品牌, SUM(销量) AS 总销量
    FROM laptops
    WHERE 品牌 != '未知品牌'
    GROUP BY 品牌
),
top5_brands AS (
    SELECT 品牌 FROM brand_total ORDER BY 总销量 DESC LIMIT 5
),
priced AS (
    SELECT
        t.品牌,
        CASE
            WHEN l.价格 < 3000 THEN '3000元以下'
            WHEN l.价格 < 5000 THEN '3000-5000元'
            WHEN l.价格 < 7000 THEN '5000-7000元'
            WHEN l.价格 < 10000 THEN '7000-10000元'
            ELSE '10000元以上'
        END AS 价格带,
        l.销量
    FROM laptops l
    INNER JOIN top5_brands t ON l.品牌 = t.品牌
)
SELECT
    品牌,
    价格带,
    COUNT(*) AS 商品数量,
    SUM(销量) AS 销量,
    ROUND(AVG(销量), 0) AS 件均销量
FROM priced
GROUP BY 品牌, 价格带
ORDER BY 品牌, 价格带;


-- ============================================================
-- 查询 9：各品牌平均价格与全市场均价对比（子查询 + CASE WHEN 标签）
-- 知识点：子查询基准值 + CASE WHEN 动态打标签
-- ============================================================
SELECT
    品牌,
    COUNT(*) AS 商品数,
    ROUND(AVG(价格), 0) AS 品牌均价,
    ROUND((SELECT AVG(价格) FROM laptops), 0) AS 市场均价,
    CASE
        WHEN AVG(价格) > (SELECT AVG(价格) FROM laptops) THEN '高于市场均价'
        ELSE '低于市场均价'
    END AS 定位标签
FROM laptops
WHERE 品牌 != '未知品牌'
GROUP BY 品牌
HAVING COUNT(*) > 5
ORDER BY 品牌均价 DESC;


-- ============================================================
-- 查询 10：笔记本类型 × 价格区间 销量矩阵（自连接 + 聚合 + 矩阵报表）
-- 知识点：交叉报表生成 + 多维聚合 + 排名
-- ============================================================
SELECT
    笔记本类型,
    SUM(CASE WHEN 价格区间 = '3000-5000元' THEN 销量 ELSE 0 END) AS 销量_3000_5000,
    SUM(CASE WHEN 价格区间 = '5000-7000元' THEN 销量 ELSE 0 END) AS 销量_5000_7000,
    SUM(CASE WHEN 价格区间 = '7000-9000元' THEN 销量 ELSE 0 END) AS 销量_7000_9000,
    SUM(CASE WHEN 价格区间 = '10000-20000元' THEN 销量 ELSE 0 END) AS 销量_10000_20000,
    SUM(销量) AS 总销量,
    RANK() OVER (ORDER BY SUM(销量) DESC) AS 类型销量排名
FROM laptops
WHERE 笔记本类型 != '其他类型'
GROUP BY 笔记本类型
ORDER BY 总销量 DESC;
