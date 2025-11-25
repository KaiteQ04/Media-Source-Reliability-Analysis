import pandas as pd
import torch

# 确保使用GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
def clean_symbol(symbol):
    # 假设clean_symbol函数只保留字符串中的数字字符
    return ''.join(filter(str.isdigit, str(symbol)))

# 读取两个文件
file2_path = "C://Users//25244//Desktop//output-2010.xlsx"
stk_listedcoinfoanl_path = "C://Users//25244//Desktop//news//上市公司基本信息年度表//STK_LISTEDCOINFOANL.xlsx"

df2 = pd.read_excel(file2_path)
df1 = pd.read_excel(stk_listedcoinfoanl_path)

# 清洗Symbol列
df1['Clean_Symbol'] = df1['Symbol'].apply(clean_symbol)
df2['Clean_Symbol'] = df2['Symbol'].apply(clean_symbol)

# 精确匹配过滤（基于清洗后的Symbol）
filtered_df = df2[~df2['Clean_Symbol'].isin(df1[df1['Clean_Symbol'].str.len() == 6]['Clean_Symbol'])]

# 移除临时列并保持原始数据格式
filtered_df = filtered_df.drop(columns=['Clean_Symbol'])

# 保存结果文件
output_path = "C://Users//25244//Desktop//delete finance st//de2010.xlsx"
filtered_df.to_excel(output_path, index=False)

print("处理完成！已删除包含指定symbol的行并保存至:", output_path)
