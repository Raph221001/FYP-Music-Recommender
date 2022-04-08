import numpy as np
import pandas
import spotipy

#Creates a popularity recommender class
class popular_recommender():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.popular_recommendations = None

        #Creates the popularity based recommender system model
        def create(self, train_data, user_id, item_id):
            self.train_data = train_data
            self.user_id = user_id
            self.item_id = item_id

            #Get a count of user_ids for each unique song as a recommendation score
            train_data_grouped = train_data.groupby([self.item_id]).agg({self.user_id: 'count'}).reset_index()
            train_data_grouped.rename(columns={user_id: 'score'}, inplace=True)

            #Songs are sorted based on the recommendation score
            train_data_sorting = train_data_grouped.sorting_values(['score', self.item_id], ascending=[0, 1])

            #Generates a recommendation rank based on the score
            train_data_sorting['Rank'] = train_data_sorting['score'].rank(ascending=0, method='first')

            #Gets the top 10 recommendations
            self.popular_recommendations = train_data_sorting.head(10)

        # Popularity based recommender system is used to make recommendations
        def recommend(self, user_id):
            user_recommendations = self.popularity_recommendations

            # Adds a user_id column which is where the recommendations are generated
            user_recommendations['user_id'] = user_id

            # Brings the user_id column to the start
            cols = user_recommendations.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            user_recommendations = user_recommendations[cols]

            return user_recommendations
