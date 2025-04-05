import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf

def normalize_data(X, y=None):
    """
    Normalize input and output data using MinMaxScaler.

    Returns:
        tuple: (scaled_X, scaler_X, scaled_y, scaler_y)
    """
    scaler_X = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler_X.fit_transform(X)

    if y is not None:
        scaler_y = MinMaxScaler(feature_range=(0, 1))
        y_scaled = scaler_y.fit_transform(y)
    else:
        scaler_y = None
        y_scaled = None

    return X_scaled, scaler_X, y_scaled, scaler_y


def inverse_transform(scaler, data):
    """
    Inverse transform the normalized data.
    """
    return scaler.inverse_transform(data)


def generate_lstm_sequences(data, time_steps):
    """
    Generate sequences for LSTM input.

    Args:
        data (np.ndarray): Normalized data (n_samples, n_features)
        time_steps (int): Sequence length

    Returns:
        tuple: (X_seq, y_seq)
    """
    X_seq, y_seq = [], []
    for i in range(len(data) - time_steps):
        X_seq.append(data[i:i + time_steps])
        y_seq.append(data[i + time_steps])
    return np.array(X_seq), np.array(y_seq)


def create_adjacency_matrix(df, threshold=0.5, method='correlation'):
    """
    Create an adjacency matrix from dataframe features.

    Args:
        df (pd.DataFrame): Feature dataframe
        threshold (float): Threshold to binarize the graph
        method (str): 'correlation' or 'distance'

    Returns:
        np.ndarray: Binary adjacency matrix (n_features x n_features)
    """
    if method == 'correlation':
        corr_matrix = df.corr().abs()
        adj_matrix = (corr_matrix > threshold).astype(float)
        np.fill_diagonal(adj_matrix.values, 0)  # no self-loop by default
        return adj_matrix.values

    elif method == 'distance':
        from sklearn.metrics.pairwise import euclidean_distances
        dist_matrix = euclidean_distances(df.T)
        normalized_dist = dist_matrix / dist_matrix.max()
        adj_matrix = (1 - normalized_dist > threshold).astype(float)
        np.fill_diagonal(adj_matrix, 0)
        return adj_matrix

    else:
        raise ValueError("Method must be 'correlation' or 'distance'")


def save_model(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    model.save(f"{path}.h5")


def load_model(path):
    return tf.keras.models.load_model(f"{path}.h5")
