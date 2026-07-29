import time
from DrissionPage import ChromiumPage# 导入自动化模块
import csv
import json

def main():
    for i in range(100):
        res = driver.listen.wait()# 等待网络响应，并从中提取JSON格式的数据
        text = res.response.body
        # 从字符串中提取 JSON 内容
        json_str = text[text.find('{'):text.rfind('}') + 1]
        # 解析 JSON,尝试获取商品列表itemsArray
        data = json.loads(json_str)
        items = data.get("data").get("itemsArray")
        # 如果没有获取到商品列表，进入一个无限循环，继续监听网络响应直到获取到有效的商品列表
        if not items:
            #设置了一个死循环，出现滑块验证后抓取不到数据，数据列表为空，继续爬取，直到不为空跳出循环，继续抓取下一页
            while 1:
                tag = 0
                try:
                    res = driver.listen.wait()# 等待数据包加载
                    text = res.response.body# 获取响应数据
                    # 解析数据，从字符串中提取 JSON 内容
                    json_str = text[text.find('{'):text.rfind('}') + 1]#查找响应文本中第一个`{`和最后一个`}`的位置，提取出JSON字符串
                    data = json.loads(json_str)#使用`json.loads()`方法将JSON字符串解析为Python数据结构
                    items = data.get("data").get("itemsArray")# 从解析后的数据中通过键值对提取`itemsArray`, 提取商品信息所在列表
                    if items:
                        tag = 1
                except Exception as e:
                    print(e)
                if tag == 1:
                    break
        # 遍历商品列表，提取商品信息，并写入CSV文件
        for item in items:
            row = []
            title = item.get("title").replace('<span class=H>','').replace('</span>','')
            row.append(title)
            price = item.get("priceWap")
            row.append(price)
            procity = item.get("procity").split(' ')
            if len(procity) > 1:
                area1 = procity[0]# 省份
                area2 = procity[1]# 城市
            else:
                area1 = procity[0]# 省份
                area2 = '未知'# 城市
            row.append(area1)
            row.append(area2)
            realSales = "NaN" if item.get("realSales") == "" else item.get("realSales").replace("人付款","")
            row.append(realSales)
            shoptitle = item.get("shopInfo").get("title")
            row.append(shoptitle)
            print(row)
            writer.writerow(row)
        print(f"======================采集完第{i+1}页=========================")
        # 进行点击搜索
        driver.ele('.next-icon next-icon-arrow-right next-xs next-btn-icon next-icon-last next-pagination-icon-next').click()
        # driver.ele('css:.next-btn-helper').click()# 会变成点击上一页
        time.sleep(3)

if __name__ == "__main__":
    f = open('data/raw_data.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(['标题','价格','省份','城市','销量','店铺'])
    driver = ChromiumPage()#  打开浏览器，初始化ChromiumPage对象，并监听特定的网络请求
    # 监听数据包
    driver.listen.start('https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/')
    url = "https://s.taobao.com/search?commend=all&ie=utf8&initiative_id=tbindexz_20170306&page=20&q=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&search_type=item&sourceId=tb.index&spm=a21bo.jianhua%2Fa.201856.d13&ssid=s5-e&tab=all"
    driver.get(url)
    main()# 调用main()函数开始数据爬取
    driver.close()