import pandas as pd

# 读取CSV文件
TB = pd.read_csv('./数据/原始数据.csv')

# 清除标题列的空格及字符，只留下文本数据和数字
# 使用正则表达式匹配文本、数字和空格，并替换其他所有字符为空字符串
TB['标题'] = TB['标题'].str.replace(r'[^\w\s\d\u4e00-\u9fa5]+', '', regex=True)
# 去除标题列中多余的空格（如果有的话）
TB['标题'] = TB['标题'].str.strip()

# 删除标题列数据重复的行
TB = TB.drop_duplicates(subset=['标题'])

# 价格列的数据都保留两位小数
if not pd.api.types.is_numeric_dtype(TB['价格']):
    TB['价格'] = pd.to_numeric(TB['价格'].str.replace(',', ''), errors='coerce')
TB['价格'] = TB['价格'].round(2)

# 对销量数据进行处理（销量数据包含“+”和“万”的字符）
# 替换“+”为空字符串
TB['销量'] = TB['销量'].str.replace('+', '')
# 如果销量中包含“万”，则替换为对应的0000
TB['销量'] = TB['销量'].str.replace('万', '0000')
# 如果销量现在是字符串类型并且包含数字，可以转换为整数
TB['销量'] = pd.to_numeric(TB['销量'], errors='coerce')

# 保存清洗后的数据
TB.to_csv('./数据/清洗后的数据.csv', index=False, encoding='utf-8-sig')