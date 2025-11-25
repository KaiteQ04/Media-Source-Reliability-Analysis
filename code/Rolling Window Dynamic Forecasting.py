import pandas as pd
import numpy as np
import statsmodels.api as sm

# 1. 读取数据并处理日期
data_path = "C://Users//25244//Desktop//2020.xlsx"
df = pd.read_excel(data_path)

# 检查必要列是否存在
required_columns = ["time", "r", "情绪得分", "NewsSource"]
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"数据文件中缺少必要的列：{required_columns}")

# 转换日期格式并排序
df["time"] = pd.to_datetime(df["time"])
df = df[(df["time"] >= '2020-01-01') & (df["time"] <= '2022-11-30')]
df = df.sort_values(["NewsSource", "time"]).reset_index(drop=True)

# 2. 按月计算每个NewsSource的β值
def calculate_monthly_beta(group):
    """按月计算β值的辅助函数"""
    group = group.set_index("time")
    monthly_beta = []

    # 按月份循环
    for month_end in pd.date_range(start=group.index.min(), end=group.index.max(), freq='M'):
        month_start = month_end - pd.offsets.MonthBegin(1)
        month_data = group.loc[month_start:month_end]

        if len(month_data) < 2:  # 至少需要2个数据点
            monthly_beta.append({"年份月份": month_end.to_period('M'), "Beta": np.nan})
            continue

        try:
            y = month_data["r"]
            X = month_data[["情绪得分"]]
            X = sm.add_constant(X)
            model = sm.OLS(y, X, missing='drop')
            results = model.fit()
            beta = results.params["情绪得分"]
            monthly_beta.append({"年份月份": month_end.to_period('M'), "Beta": beta})
        except Exception as e:
            print(f"计算NewsSource: {group['NewsSource'].iloc[0]}在{month_end}的β值时出错: {e}")
            monthly_beta.append({"年份月份": month_end.to_period('M'), "Beta": np.nan})

    return pd.DataFrame(monthly_beta)

# 对每个NewsSource分组计算
beta_dfs = []
for news_source, group in df.groupby("NewsSource"):
    beta_df = calculate_monthly_beta(group)
    beta_df["NewsSource"] = news_source
    beta_dfs.append(beta_df)

monthly_beta_df = pd.concat(beta_dfs).reset_index(drop=True)

# 3. 滚动预测功能
def generate_rolling_predictions(beta_df):
    """生成滚动预测"""
    beta_df = beta_df.sort_values("年份月份")

    # 计算滚动窗口均值（使用过去数据预测下月）
    beta_df["预测_18个月"] = (
        beta_df["Beta"]
        .rolling(window=18, min_periods=1, closed='left')
        .mean()
        .shift(1)
    )

    beta_df["预测_12个月"] = (
        beta_df["Beta"]
        .rolling(window=12, min_periods=1, closed='left')
        .mean()
        .shift(1)
    )

    beta_df["预测_6个月"] = (
        beta_df["Beta"]
        .rolling(window=6, min_periods=1, closed='left')
        .mean()
        .shift(1)
    )

    return beta_df

# 对每个NewsSource生成预测
pred_dfs = []
for news_source, group in monthly_beta_df.groupby("NewsSource"):
    pred_df = generate_rolling_predictions(group)
    pred_dfs.append(pred_df)

predictions_df = pd.concat(pred_dfs).reset_index(drop=True)

# 添加预测月份列
predictions_df["预测月份"] = predictions_df["年份月份"] + 1

# 4. 格式化输出结果
# 格式化β值结果
monthly_beta_df["年份月份"] = monthly_beta_df["年份月份"].dt.strftime("%Y-%m")

# 格式化预测结果
predictions_df["预测月份"] = predictions_df["预测月份"].dt.strftime("%Y-%m")
predictions_output = predictions_df[["NewsSource", "预测月份", "预测_18个月", "预测_12个月", "预测_6个月"]]

# 筛选2022年1-12月的预测结果
predictions_output = predictions_output[
    (predictions_output["预测月份"] >= "2022-01") &
    (predictions_output["预测月份"] <= "2022-12")
]
# 去除可能存在的重复值
predictions_output = predictions_output.drop_duplicates(
    subset=["NewsSource", "预测月份"],
    keep='last'
)

# 5. 保存结果到两个文件
# 保存β值结果
beta_output_path = "C://Users//25244//Desktop//beta_values.xlsx"
monthly_beta_df.to_excel(beta_output_path, index=False)

# 保存预测结果
predictions_output_path = "C://Users//25244//Desktop//predictions.xlsx"
predictions_output.to_excel(predictions_output_path, index=False)

print(f"β值结果已保存至 {beta_output_path}")
print(f"预测结果已保存至 {predictions_output_path}")