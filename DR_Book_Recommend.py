
#Import Libraries
import pandas as pd
import streamlit as st 
from pickle import load
import time
from PIL import Image
from IPython.core.display import HTML
from PIL import Image


#Image on webpage
img = Image.open("grt.jpg")
st.image(img)#, use_column_width=True)
img2 = Image.open("YourRecommendations-Recolor.png")


#Model Loading
user_similarity = load(open('Matrix.pkl', 'rb'))
pt = load(open('Pivot.pkl', 'rb'))
df = load(open('df.pkl', 'rb'))
popular_df = load(open('popular.pkl', 'rb'))
userid = load(open('usersid.pkl', 'rb'))


#User Input Parameters
picked_userid = st.selectbox("Select the userid", options = userid, index = 58635)
t = st.number_input("Enter the books to recommend",min_value=5, max_value=20, step=1)


#Defining a function to load images
def path_to_image_html(path):
    return '<img src="'+ path + '" >'

def pop_load_Image(df):
     return HTML(df[['Image-URL-M', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Book-Rating']].to_html(formatters={'Image-URL-M': path_to_image_html}, escape=False))
 
def pop_load_DF(df):
    return HTML(df[['Image-URL-M', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Book-Rating']].to_html(formatters={'Image-URL-M': path_to_image_html}, escape=False))    


#Defining the function for the recommendation engine
if st.button('Recommend'):
    with st.image(img2):
        time.sleep(0.85)
        st.markdown(f'**_Top {t} recommendation for {picked_userid}_**')
        
    if picked_userid not in pt.index:
        d = popular_df[popular_df['num_ratings']>=100].sort_values('avg_rating',ascending=False).head(t)
        d = d[['Image-URL-M', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Book-Rating']]
        d = d.reset_index()
        rs = pop_load_Image(d)
        rs
        
    else: 
    
    
        def get_user_similarity(User_id):
            # Pick a user ID
        
            picked_userid = User_id
        
            # Remove picked user ID from the user list
            user_similarity.drop(index = picked_userid, inplace=True)
        
            # Take a look at the data
            return user_similarity.head()
        
        #Reviewing the function
        get_user_similarity(picked_userid)
        
        
        #Defining a function for retrieving the similar users to any given input user-id
        q = 15
        
        def get_similar_users(picked_userid):
            #Number of similar users
            n = q
        
            # User similarity threashold
            user_similarity_threshold = 0.3
        
            # Get top n similar users
            similar_users = user_similarity[user_similarity[picked_userid]>user_similarity_threshold][picked_userid].sort_values(ascending=False)[:n]
        
        
            return similar_users
        #Reviewing the function
        similar_users = get_similar_users(picked_userid)
        
        #Defining the function for removing the books which has Nan in entire column
        def read_books_userid(picked_userid):
            
                    
            # Books that the target user has read
            picked_userid_read = pt[pt.index == picked_userid].dropna(axis=1, how='all')
            
            return picked_userid_read
        
        #Reviewing the function
        picked_userid_read = read_books_userid(picked_userid)
        
        #Defining the function for fetching the books read by similar users excluding Nan rated books
        def sim_userbooks(similar_users):
              
            # books that similar users read. Remove books that none of the similar users have read
              similar_user_books = pt[pt.index.isin(similar_users.index)].dropna(axis=1, how='all')
              
              return similar_user_books
        
        #Reviewing the function 
        similar_user_books = sim_userbooks(similar_users)
        
        #Defining a function for excluding target user read books from similar users books dataset
        def user_dropped_data(similar_user_books, picked_userid_read):
            # Remove the read book from the book list
            drop_user_books = similar_user_books.drop(picked_userid_read.columns,axis=1, inplace=False, errors='ignore')
        
            # Take a look at the data
            return drop_user_books
        
        #Reviewing the function
        drop_user_books = user_dropped_data(similar_user_books, picked_userid_read)
        
        
        #Defining the function for fetching the top 5 rated books read by similar users
        
        def user_collaborative_recommendation(similar_user_books):
              
              
            # A dictionary to store item scores
              item_score = {}
        
            # Loop through items
              for i in similar_user_books.columns:
                    
                    
                  # Get the ratings for book i
                    book_rating = similar_user_books[i]
                    
                    
                  # Create a variable to store the score
                    total = 0
                  # Create a variable to store the number of scores
                    count = 0
                    
                  # Loop through similar users
                    for u in similar_users.index:
                          
                          
                          
                        # If the book has rating
                          if pd.isna(book_rating[u]) == False:
                                                                
                        # Score is the sum of user similarity score multiply by the book rating
                                score = similar_users[u] * book_rating[u]
                          
                        # Add the score to the total score for the book so far
                                total += score
                          
                        # Add 1 to the count
                                count +=1
                          
            # Get the average score for the item
                    item_score[i] = total / count
        
            # Convert dictionary to pandas dataframe
              item_score = pd.DataFrame(item_score.items(), columns=['Book-Title', 'Book_score'])
        
            # Sort the books by score
              ranked_item_score = item_score.sort_values(by='Book_score', ascending=False)
        
            # Select top m books
              m = t
              
              return ranked_item_score.head(m)
        
        
        #Final Recommendation to the target user w.r.t top rated books by similar users excluding read books
        def recom_actual(drop_user_books):
            
            #pd.set_option('display.max_colwidth', None)
            
            actual_recommendation=user_collaborative_recommendation(drop_user_books)
            
            return actual_recommendation
        
        #Reviewing the function
        actual_recommendation = recom_actual(drop_user_books)
        
        #Extracting the columns 
        df.keys()
        
        #Extracting the max ratings from the dataset
        rr = df.groupby(by='Book-Title', as_index=False)[df.keys()[:]].max()
        
        #Merging the columns to recommendation for more info about the recommended book
        ar = actual_recommendation.merge(rr, how='inner', on='Book-Title')
        
        #Arranging the columns
        ar = ar[['Image-URL-M', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Book-Rating']]
        
        #Defining a function to load images
        
        def load_Image(df):
             return HTML(df[['Image-URL-M', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Book-Rating']].to_html(formatters={'Image-URL-M': path_to_image_html}, escape=False))
            
        def load_DF(df):
            return HTML(df[['Image-URL-M', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Book-Rating']].to_html(formatters={'Image-URL-M': path_to_image_html}, escape=False))
        
        #Viewing the Final User-User Recommendation with full info
        result = load_DF(ar)
        
        rs = result
        rs
