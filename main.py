
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

#convert text into vectors
from sklearn.feature_extraction.text import CountVectorizer
cv=CountVectorizer(max_features=5000, stop_words='english')
vectors=cv.fit_transform(new_df['tags']).toarray()

#similirity calculation 
from sklearn.metrics.pairwise import cosine_similarity
similarity=cosine_similarity(vectors)

 
#improved function
def recommend(movie):
  movie=movie.lower()

  #check if movie exists
  if movie not in new_df['title'].str.lower().values:
    return["Movie not Found"]

  #get index safely
  movie_index=new_df[new_df['title'].str.lower()==movie].index[0]

  distances=similarity[movie_index]

  movie_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x: x[1])[1:6]

  recommendations=[]
  for i in movie_list:
    recommendations.append(new_df.iloc[i[0]].title)
  
  return recommendations
       
# print(recommend("Avatar"))

import nltk
from nltk.stem.porter import PorterStemmer

ps=PorterStemmer()

#ceate steaming function
def stem(text):
  y=[]

  for i in text.split():
    y.append(ps.stem(i))

  return " ".join(y)

#apply steamming to tags
new_df['tags']=new_df['tags'].apply(stem)

#rebuild
from sklearn.feature_extraction.text import CountVectorizer

cv=CountVectorizer(max_features=5000, stop_words='english')
vectors=cv.fit_transform(new_df['tags']).toarray()

from sklearn.metrics.pairwise import cosine_similarity
similarity=cosine_similarity(vectors)

# print(recommend("toy story"))
# print(recommend("inception"))

#remove overview from tags
merged_df['tags']=merged_df['genres']+merged_df['keywords']+merged_df['cast']+merged_df['crew']

#convert list into string
new_df=merged_df[['movie_id','title','tags']]
new_df['tags']=new_df['tags'].apply(lambda x:" ".join(x))

#lower case
new_df['tags']=new_df['tags'].apply(lambda x: x.lower())

new_df['tags']=new_df['tags'].apply(stem)

from sklearn.feature_extraction.text import CountVectorizer

cv=CountVectorizer(max_features=5000, stop_words='english')
vectors=cv.fit_transform(new_df['tags']).toarray()

from sklearn.metrics.pairwise import cosine_distances
similarity=cosine_similarity(vectors)

# print(recommend("toy story"))
# print(recommend("inception"))

from sklearn.feature_extraction.text import TfidfVectorizer

#create object
tfidf=TfidfVectorizer(max_features=5000, stop_words='english')
#convert text to vectors
vectors=tfidf.fit_transform(new_df['tags']).toarray()

from sklearn.metrics.pairwise import cosine_similarity
similarity=cosine_similarity(vectors)


print(recommend("toy story"))
print(recommend("inception"))