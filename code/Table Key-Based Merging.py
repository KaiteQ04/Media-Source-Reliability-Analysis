import pandas as pd


def enhanced_excel_merge(file1_path, file2_path, output_path):
    """
    增强版Excel合并方案，特点：
    1. 先合并后处理重复列（保留右表列）
    2. 优化内存处理
    3. 数据验证机制
    4. 智能类型转换
    5. 匹配出现缺失值时，直接舍弃
    """
    try:
        # 读取数据（指定NewsID为字符串类型）
        df_news = pd.read_excel(file1_path, dtype={'NewsID': 'string'})
        df_security = pd.read_excel(file2_path, dtype={'NewsID': 'string'})

        # 标准化列名（去除前后空格和特殊字符，替换空格为下划线）
        df_news.columns = df_news.columns.str.strip().str.replace(r'\s+', '_', regex=True)
        df_security.columns = df_security.columns.str.strip().str.replace(r'\s+', '_', regex=True)

        # 数据预处理
        for df in [df_news, df_security]:
            df['NewsID'] = df['NewsID'].astype('string').str.strip()

        # 去除右表中NewsID的重复值
        df_security = df_security.drop_duplicates(subset='NewsID')

        # 执行右连接合并，添加后缀以区分重复列
        merged_df = pd.merge(
            left=df_news,
            right=df_security,
            on='NewsID',
            how='right',
            suffixes=('_left', ''),  # 右表列名保持不变，左表重复列加'_left'
            validate='many_to_one'  # 确保右表NewsID唯一
        )

        # 处理重复列：删除左表重复列（以'_left'结尾的列）
        cols_to_drop = [col for col in merged_df.columns if col.endswith('_left')]
        merged_df = merged_df.drop(columns=cols_to_drop)

        # 记录并打印被移除的重复列
        duplicate_cols = list({col[:-5] for col in cols_to_drop})  # 提取原列名
        if duplicate_cols:
            print(f"已自动移除左表的重复列：{', '.join(duplicate_cols)}")

        # 验证合并结果完整性（右连接应保留所有右表行）
        # 检查左表关键列是否存在空值（即未匹配到的记录）
        missing_mask = merged_df[df_news.columns.difference(['NewsID'])].isna().all(axis=1)
        if missing_mask.any():
            merged_df = merged_df[~missing_mask]
            print(f"警告：已舍弃{missing_mask.sum()}条无法匹配的左表记录")

        # 优化输出
        merged_df.to_excel(output_path, index=False, sheet_name='合并结果')
        print(f"合并成功！文件已保存至：{output_path}")
        return True

    except Exception as e:
        print(f"合并失败：{str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    news_info = "C:/Users/25244/Desktop/news/新闻基本信息表/新闻基本信息表2022/News_NewsInfo.xlsx"
    security_info = "C:/Users/25244/Desktop/news/新闻证券关联表/新闻证券关联表2022/News_Security.xlsx"
    output_path = "C:/Users/25244/Desktop/2022.xlsx"

    enhanced_excel_merge(news_info, security_info, output_path)