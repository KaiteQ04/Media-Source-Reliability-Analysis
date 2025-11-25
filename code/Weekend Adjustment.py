import pandas as pd
from datetime import timedelta

# 读取文件
news_df = pd.read_excel("C:\\Users\\HP\\Desktop\\金融大数据news\\de2022.xlsx")
returns_df = pd.read_excel("C:\\Users\\HP\\Desktop\\金融大数据news\\2022收益率_调整后.xlsx")
market_df = pd.read_excel("C:\\Users\\HP\\Desktop\\金融大数据news\\沪深300指数历史数据 .xlsx")


# 确保列名一致
news_df['time'] = pd.to_datetime(news_df['time'])
returns_df['time'] = pd.to_datetime(returns_df['time'])
market_df['日期'] = pd.to_datetime(market_df['日期'])
market_df = market_df.rename(columns={'日期': 'time'})  # 重命名为统一的列名

# 确保股票代码为字符串，保留前导零
news_df['Stkcd'] = news_df['Stkcd'].astype(str).str.zfill(6)
returns_df['Stkcd'] = returns_df['Stkcd'].astype(str).str.zfill(6)

# 生成所有交易日列表
trade_dates = sorted(returns_df['time'].unique())

# 创建一个新闻日期到最近下一个交易日的映射
def get_next_trade_date(news_date):
    for d in trade_dates:
        if d > news_date:
            return d
    return None  # 没有下一个交易日（比如年底）

# 创建合并时间列：即情绪得分对应的目标收益率日期
news_df['match_time'] = news_df['time'].apply(get_next_trade_date)

# 合并新闻与个股收益
merged_df = pd.merge(
    news_df,
    returns_df,
    left_on=['Stkcd', 'match_time'],
    right_on=['Stkcd', 'time'],
    how='inner'
)

# 再与市场收益率合并
merged_df = pd.merge(
    merged_df,
    market_df,
    left_on='match_time',   # 即 returns 中的时间，也就是 next_trade_date
    right_on='time',
    how='left'
)

# 计算超额收益率
merged_df['r'] = merged_df['Dretwd'] - merged_df['涨跌幅']

# 选取并重命名字段
result_df = merged_df[['time', 'NewsSource', 'r', 'Stkcd', '情绪得分']]
result_df = result_df.rename(columns={
    'Stkcd': 'symbol'
})
result_df['time'] = result_df['time'].dt.date  # 去掉小时分钟

# 过滤数量过少的新闻源
final_counts = result_df['NewsSource'].value_counts()
valid_final_sources = final_counts[final_counts >= 20].index
result_df = result_df[result_df['NewsSource'].isin(valid_final_sources)]

# 保存
result_df.to_excel("C:\\Users\\HP\\Desktop\\金融大数据news\\媒体情绪与次日收益合并结果new.xlsx", index=False)
print("合并完成，文件已保存为: 媒体情绪与次日收益合并结果new.xlsx")

