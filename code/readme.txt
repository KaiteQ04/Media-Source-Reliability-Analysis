1、Table Key-Based Merging
Merged the news basic information table with the news–security linkage table using the NewsID field through a right join. This produces a complete dataset with consistent keys. Duplicate columns were removed to ensure clean and reliable input data for subsequent processing.

2、Data Cleaning 
Cross-checked stock codes with the listed company information table and removed ST companies and financial institutions. This ensures that the analysis focuses only on normally operating, non-financial firms, preventing bias caused by the special accounting and regulatory nature of financial-sector companies.

3、Sentiment Analysis (FinBERT-Chinese)
Applied a pre-trained FinBERT Chinese financial sentiment model to perform sentence-level sentiment classification (neutral, positive, negative). Sentences were segmented, classified individually, and aggregated to compute overall sentiment scores for each news article, providing quantitative sentiment indicators for downstream modeling.

4、Weekend Adjustment: Time Alignment & Abnormal Return Calculation
Mapped each news timestamp to the next valid trading day, ensuring correct alignment between non-trading day news (e.g., weekends) and market data. Merged individual stock returns with CSI300 index returns and computed abnormal returns (AR). Generated a time-aligned dataset suitable for causal sentiment–return analysis.

5、Static β Regression and Standardization
Grouped the dataset by NewsSource and implemented univariate linear regression to evaluate the marginal impact of sentiment score on abnormal returns. Extracted static β coefficients for each media outlet. Standardized β values to obtain influence weights used to quantify the relative impact of different media sources.

6、Rolling Window Dynamic Forecasting
Constructed a monthly time series of historical β values for each media outlet. Applied rolling windows of 6 / 12 / 18 months to dynamically compute predicted β coefficients. This captures the time-varying characteristics of media influence and provides multi-scale forecasts of media reliability trends.