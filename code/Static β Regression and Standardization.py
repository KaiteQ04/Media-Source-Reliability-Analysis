import pandas as pd
import numpy as np
import statsmodels.api as sm

# 1. 读取数据
data_path = "C://Users//25244//Desktop//2022.xlsx"  # 假设为Excel文件
df = pd.read_excel(data_path)

# 检查列是否存在
required_columns = ["r", "情绪得分", "NewsSource"]
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"数据文件中缺少必要的列：{required_columns}")

# 2. 按 NewsSource 分组并进行回归分析
beta_values = {}  # 用于存储每个 NewsSource 对应的 β 值

for news_source, group in df.groupby("NewsSource"):
    # 提取因变量（ri）和自变量（Score_i）
    y = group["r"]
    X = group["情绪得分"]
    X = sm.add_constant(X)  # 添加截距项

    # 拟合线性回归模型
    model = sm.OLS(y, X)
    results = model.fit()

    # 获取回归系数 B_j（即 β 值）
    beta = results.params["情绪得分"]
    beta_values[news_source] = beta

# 3. 标准化 β 值
B_values = np.array(list(beta_values.values()))  # 将所有 β 值转为数组
mean_B = B_values.mean()
std_B = B_values.std()
w_j = (B_values - mean_B) / std_B

# 创建一个包含 β 值和标准化权重的 DataFrame
results_df = pd.DataFrame({
    "NewsSource": list(beta_values.keys()),
    "β 值": B_values,
    "标准化后的权重 w_j": w_j
})

# 4. 将 β 值和标准化权重添加到原始数据框中
# 创建一个与原始数据框索引对应的 β 列
df["β 值"] = df["NewsSource"].map(beta_values)

# 将标准化后的权重 w_j 添加到原始数据框中
df["标准化后的权重 w_j"] = df["NewsSource"].map(dict(zip(list(beta_values.keys()), w_j)))

# 确保 β 值和标准化后的权重只在每个 NewsSource 的第一个单元格中出现
df.loc[df.groupby("NewsSource").cumcount() > 0, ["β 值", "标准化后的权重 w_j"]] = np.nan

# 5. 将结果添加到原始数据框的末尾
df_with_results = pd.concat([df, results_df], ignore_index=True)

# 6. 保存新的 Excel 文件
output_path = "C://Users//25244//Desktop//beta_2022.xlsx"
df_with_results.to_excel(output_path, index=False)

print(f"结果已保存到 {output_path}")
