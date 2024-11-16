import pandas as pd

df = pd.read_csv('players.csv')
df['full_name'] = df['first_name'] + ' ' + df['last_name']

print(df.head())
df.to_csv('players.csv')