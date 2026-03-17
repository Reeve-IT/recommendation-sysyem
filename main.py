import pandas as pd

df=pd.read_csv("data/tmdb_5000_movies.csv")
print(df.head())
print(df.info())
print(df.describe())