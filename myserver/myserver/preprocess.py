import pandas as pd

# 1. Read your CSV
df = pd.read_csv('arima_test_predictions.csv')  # replace with your filename

# 2. Remove brackets from the “Actual” column and cast to float
df['Actual'] = (
    df['Actual']
    .str.replace(r'[\[\]]', '', regex=True)  # remove “[]”
    .astype(float)
)

# 3. (Optional) Inspect
print(df.head())

# 4. Save back out
df.to_csv('predictions_clean.csv', index=False)
