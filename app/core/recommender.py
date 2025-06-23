from uuid import UUID

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from typing import List, Dict
from scipy.sparse import csr_matrix , coo_matrix
import implicit


class BookRecommender:
    def __init__(self):
        self.user_ratings = None
        self.book_features = None
        self.collab_model = None
        self.content_model = None
        self.tfidf_matrix = None
        self.book_id_to_index = {}
        self.index_to_book_id = {}
        self.user_mapping = {}
        self.item_mapping = {}
        self.user_inverse_mapping = {}
        self.item_inverse_mapping = {}
        self.user_item_matrix = None
        self.model = None

    def load_data(self, ratings_df: pd.DataFrame, books_df: pd.DataFrame):
        """Load and preprocess data"""
        self.user_ratings = ratings_df
        self.book_features = books_df

        # Create mappings
        self.book_id_to_index = {bid: idx for idx, bid in enumerate(books_df['id'])}
        self.index_to_book_id = {v: k for k, v in self.book_id_to_index.items()}

    def train_collaborative(self):
        """Train collaborative filtering model"""
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            self.user_ratings[['user_id', 'book_id', 'rating']],
            reader
        )
        trainset, _ = train_test_split(data, test_size=0.2)
        self.collab_model = KNNBasic(sim_options={'name': 'cosine', 'user_based': False})
        self.collab_model.fit(trainset)

    def train_content_based(self):
        """Train content-based model"""
        tfidf = TfidfVectorizer(stop_words='english')
        combined_features = (
                self.book_features['title'] + " " +
                self.book_features['author'] + " " +
                self.book_features['genres'].apply(lambda x: ' '.join(x))
        )
        self.tfidf_matrix = tfidf.fit_transform(combined_features)
        self.content_model = cosine_similarity(self.tfidf_matrix)

    def hybrid_recommend(self, user_id: UUID, top_n: int = 5) -> List[Dict]:
        """Generate hybrid recommendations"""
        # Get collaborative predictions
        collab_recs = []
        for book_id in self.book_features['id']:
            pred = self.collab_model.predict(user_id, book_id)
            collab_recs.append((book_id, pred.est))

        # Get content-based scores for user's rated books
        user_rated = self.user_ratings[self.user_ratings['user_id'] == user_id]
        if len(user_rated) > 0:
            avg_content_scores = np.zeros(len(self.book_features))
            for _, row in user_rated.iterrows():
                book_idx = self.book_id_to_index[row['book_id']]
                content_scores = self.content_model[book_idx]
                weighted_scores = content_scores * row['rating']
                avg_content_scores += weighted_scores
            avg_content_scores /= len(user_rated)
        else:
            avg_content_scores = np.zeros(len(self.book_features))

        # Combine scores
        recommendations = []
        for book_id, collab_score in collab_recs:
            book_idx = self.book_id_to_index[book_id]
            hybrid_score = 0.6 * collab_score + 0.4 * avg_content_scores[book_idx]
            recommendations.append((book_id, hybrid_score))

        # Sort and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [{
            'book_id': book_id,
            'score': score,
            'title': self.book_features[self.book_features['id'] == book_id]['title'].values[0],
            'author': self.book_features[self.book_features['id'] == book_id]['author'].values[0]
        } for book_id, score in recommendations[:top_n]]

    def get_similar_books(self, book_id: UUID, top_n: int = 5) -> List[Dict]:
        """Content-based similar books"""
        book_idx = self.book_id_to_index[book_id]
        sim_scores = list(enumerate(self.content_model[book_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n + 1]
        return [{
            'book_id': self.index_to_book_id[idx],
            'score': score,
            'title': self.book_features.iloc[idx]['title'],
            'author': self.book_features.iloc[idx]['author']
        } for idx, score in sim_scores]

    def train_als(self, factors=50, iterations=15, regularization=0.01):
        """Train ALS model using implicit library"""
        # Create mappings for user and item IDs
        unique_users = self.user_ratings['user_id'].unique()
        unique_items = self.user_ratings['book_id'].unique()

        self.user_mapping = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.item_mapping = {item_id: idx for idx, item_id in enumerate(unique_items)}
        self.user_inverse_mapping = {idx: user_id for user_id, idx in self.user_mapping.items()}
        self.item_inverse_mapping = {idx: item_id for item_id, idx in self.item_mapping.items()}

        # Create sparse user-item matrix in COO format (then convert to CSR)
        rows = self.user_ratings['user_id'].map(self.user_mapping)
        cols = self.user_ratings['book_id'].map(self.item_mapping)
        ratings = self.user_ratings['rating'].values

        self.user_item_matrix = coo_matrix((ratings, (rows, cols)),
                                           shape=(len(unique_users), len(unique_items))).tocsr()

        # Train ALS model
        self.model = implicit.als.AlternatingLeastSquares(
            factors=factors,
            iterations=iterations,
            regularization=regularization,
            random_state=42
        )

        # Fit the model (implicit expects confidence values, so we pass the ratings directly)
        self.model.fit(self.user_item_matrix)

    def als_recommend(self, user_id, n=5):
        """Get top-N recommendations for a user"""
        if user_id not in self.user_mapping:
            raise ValueError(f"User {user_id} not found in training data")

        user_idx = self.user_mapping[user_id]

        # Get recommendations - returns (item_indices, scores) tuple
        item_indices, _ = self.model.recommend(
            userid=user_idx,
            user_items=self.user_item_matrix[user_idx],
            N=n,
            filter_already_liked_items=True
        )

        # Convert indices back to UUIDs
        return [self.item_inverse_mapping[item_idx] for item_idx in item_indices]

