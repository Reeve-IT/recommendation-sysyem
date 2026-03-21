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

# print(merged_df.head())
# print(merged_df.shape)

import ast
#convert string into list
merged_df['genres']=merged_df['genres'].apply(ast.literal_eval)
merged_df['keywords']=merged_df['keywords'].apply(ast.literal_eval)
merged_df['cast']=merged_df['cast'].apply(ast.literal_eval)
merged_df['crew']=merged_df['crew'].apply(ast.literal_eval)

#extracting names 
def extract_names(obj):
  names=[]
  for i in obj:
    names.append(i['name'])
  return names

merged_df['genres']=merged_df['genres'].apply(extract_names)
merged_df['keywords']=merged_df['keywords'].apply(extract_names)

#extracting top cast
def extract_top_cast(obj):
  names=[]
  for i in obj[:3]:#top 3 actors
     names.append(i['name'])
  return names

merged_df['cast']=merged_df['cast'].apply(extract_top_cast)

#extract director name
def fetch_director(obj):
  names=[]
  for i in obj:
    if i['job']=='Director':
      return[i['name']]
  return[]
merged_df['crew']=merged_df['crew'].apply(fetch_director)

#print(merged_df[['genres','keywords','cast','crew']].head())

#remove spaces from names
def remove_spaces(lst):
  return[i.replace(" ","")for i in lst]
merged_df['genres']=merged_df['genres'].apply(remove_spaces)
merged_df['keywords']=merged_df['keywords'].apply(remove_spaces)
merged_df['cast']=merged_df['cast'].apply(remove_spaces)
merged_df['crew']=merged_df['crew'].apply(remove_spaces)

#convert overview into list
merged_df['overview']=merged_df['overview'].apply(lambda x:x.split())

#create final tags column
merged_df['tags']=merged_df['overview']+merged_df['genres']+merged_df['keywords']+merged_df['cast']+merged_df['crew']

#convert list into string
merged_df['tags']=merged_df['tags'].apply(lambda x:" ".join(x))

#clean data set
new_df=merged_df[['movie_id','title','tags']]

#print(new_df.head())

#convert into lower case 
new_df['tags']=new_df['tags'].apply(lambda x: x.lower())