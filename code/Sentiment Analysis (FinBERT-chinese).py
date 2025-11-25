import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import re

# 确保使用GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 下载并加载FinBERT模型和tokenizer
model_name = "yiyanghkust/finbert-tone-chinese"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)
model.to(device)  # 将模型移动到GPU

# 读取Excel文件
input_path = "C://Users//25244//Desktop//news//预处理//2010.xlsx"
output_path = "C://Users//25244//Desktop//output-2010.xlsx"
df = pd.read_excel(input_path, usecols=["NewsContent"])

# 情感标签映射
sentiment_labels = ["中性", "正面", "负面"]

# 创建包含权重列的结果DataFrame
result_columns = [
    "单元格索引",
    "中性句子个数",
    "正面句子个数",
    "负面句子个数",
    "中性权重",
    "正面权重",
    "负面权重"
]
result_df = pd.DataFrame(columns=result_columns)

# 分句的正则表达式
sentence_split_pattern = re.compile(r'(?<=[。！？])')

# 遍历每一行
for index, row in df.iterrows():
    text = row["NewsContent"]
    # 检查text是否为字符串
    if isinstance(text, str):
        sentences = sentence_split_pattern.split(text)  # 分句
        sentiment_counts = {"中性": 0, "正面": 0, "负面": 0}

        # 对每个句子进行情感分析
        for sentence in sentences:
            if sentence.strip():  # 去除空句子
                inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True, max_length=512)
                inputs = {k: v.to(device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = model(**inputs)
                    logits = outputs.logits
                predictions = torch.argmax(logits, dim=-1)
                sentiment = sentiment_labels[predictions.item()]
                sentiment_counts[sentiment] += 1

        # 计算情感权重
        total_sentences = sum(sentiment_counts.values())
        if total_sentences > 0:
            neutral_weight = round(sentiment_counts["中性"] / total_sentences, 4)
            positive_weight = round(sentiment_counts["正面"] / total_sentences, 4)
            negative_weight = round(sentiment_counts["负面"] / total_sentences, 4)
        else:
            neutral_weight = positive_weight = negative_weight = 0.0

        # 添加结果到DataFrame
        result_df = pd.concat([result_df, pd.DataFrame({
            "单元格索引": [index + 2],
            "中性句子个数": [sentiment_counts["中性"]],
            "正面句子个数": [sentiment_counts["正面"]],
            "负面句子个数": [sentiment_counts["负面"]],
            "中性权重": [neutral_weight],
            "正面权重": [positive_weight],
            "负面权重": [negative_weight]
        })], ignore_index=True)
    else:
        print(f"行 {index + 2} 的 NewsContent 不是字符串，跳过此行")
# 将结果写入新的Excel文件
result_df.to_excel(output_path, index=False)
print(f"结果已保存到 {output_path}")
