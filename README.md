# Media-Source-Reliability-Analysis
Quantifying the Impact of Financial News Sentiment on Stock Abnormal Returns (2010–2022)

A full-stack financial text analysis project evaluating media reliability via sentiment–return modeling and dynamic β estimation.

In financial markets, news media significantly influence investor sentiment and stock reactions. This project evaluates the reliability, influence, and credibility of financial news media sources by analyzing how media sentiment affects stock abnormal returns. It builds a full financial data science pipeline including text analysis, FinBERT-based sentiment modeling, event-study AR construction, OLS regression, and it further extends to a rolling-window dynamic β model to capture time-varying media influence.

Project Overview:
News → Text preprocessing

FinBERT sentiment scoring

News–trading-day alignment

Abnormal return (AR) calculation

Media-level regression modeling

Rolling-window prediction of time-varying influence

The final output is a media-level influence score (β & standardized weight ω).
