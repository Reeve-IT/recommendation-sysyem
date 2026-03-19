#first activate venv by .\venv\Scripts\Activate

import pandas as pd

df=pd.read_csv("data/tmdb_5000_movies.csv")
credit=pd.read_csv("data/tmdb_5000_credits.csv")
# print(df.head())
# print(credit.head())
# print(df.info())
# print(df.describe())
# print(df.isna().sum())

#merging both csv
merged_df=pd.merge(df,credit, on='title')

#select only required columns
merged_df=merged_df[['id','title','overview','genres','keywords','cast','crew']]

#rename id to movie_id
merged_df=merged_df.rename(columns={'id':'movie_id'})

#drop rows with missing values
merged_df=merged_df.dropna()

#clean structure
merged_df=merged_df.reset_index(drop=True)

print(merged_df.head())
print(merged_df.shape)