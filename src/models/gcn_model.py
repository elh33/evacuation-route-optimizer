"""GCN model for time-series prediction of weather and traffic conditions."""
import os
import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from spektral.layers import GCNConv
from tensorflow.keras import layers, models, callbacks

from config import GCN_PARAMS, PROCESSED_DATA_DIR, GCN_MODEL_DIR

logger = logging.getLogger(__name__)

class WeatherTrafficGCN:
    """GCN model for predicting weather and traffic conditions."""
    
    def __init__(self, 
                 input_shape, 
                 output_shape, 
                 adj_matrix,
                 units=GCN_PARAMS["units"],
                 dropout=GCN_PARAMS["dropout"],
                 activation=GCN_PARAMS["activation"]):
        """
        Initialize the GCN model.
        
        Args:
            input_shape (tuple): Shape of input data (nodes, features)
            output_shape (int): Number of output features
            adj_matrix (np.ndarray): Adjacency matrix (symmetric)
            units (int): Number of GCN units
            dropout (float): Dropout rate
            activation (str): Activation function
        """
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.adj_matrix = adj_matrix
        self.units = units
        self.dropout = dropout
        self.activation = activation

        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()
        self.model = self._build_model()

    def _build_model(self):
        """
        Build the GCN model architecture.
        
        Returns:
            tensorflow.keras.Model: Compiled GCN model
        """
        X_input = layers.Input(shape=self.input_shape)
        A_input = layers.Input((self.input_shape[0],))

        x = GCNConv(self.units, activation=self.activation)([X_input, A_input])
        x = layers.Dropout(self.dropout)(x)
        x = GCNConv(self.units // 2, activation=self.activation)([x, A_input])
        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dense(self.units // 4, activation='relu')(x)
        output = layers.Dense(self.output_shape)(x)

        model = models.Model(inputs=[X_input, A_input], outputs=output)
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        return model

    def train(self, X, y, epochs=100, batch_size=32, validation_split=0.2):
        """
        Train the GCN model.
        
        Args:
            X (np.ndarray): Input node features (samples, nodes, features)
            y (np.ndarray): Target values (samples, output_shape)
            epochs (int): Number of training epochs
            batch_size (int): Batch size
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            tensorflow.keras.callbacks.History: Training history
        """
        X_scaled = self.scaler_X.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
        y_scaled = self.scaler_y.fit_transform(y)

        A = np.repeat(self.adj_matrix[np.newaxis, :, :], X.shape[0], axis=0)

        X_train, X_val, y_train, y_val, A_train, A_val = train_test_split(
            X_scaled, y_scaled, A, test_size=validation_split, random_state=42
        )

        early_stop = callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)

        history = self.model.fit(
            [X_train, A_train], y_train,
            validation_data=([X_val, A_val], y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=1
        )

        return history

    def predict(self, X):
        """
        Make predictions using the GCN model.
        
        Args:
            X (np.ndarray): Input features (nodes, features)
            
        Returns:
            np.ndarray: Predicted values
        """
        X_scaled = self.scaler_X.transform(X.reshape(-1, X.shape[-1])).reshape(1, *X.shape)
        A = self.adj_matrix[np.newaxis, :, :]
        y_pred_scaled = self.model.predict([X_scaled, A])
        return self.scaler_y.inverse_transform(y_pred_scaled)

    def save(self, path):
        """
        Save the model and scalers.
        
        Args:
            path (str): Path to save the model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(f"{path}.h5")

        np.save(f"{path}_scaler_X.npy", self.scaler_X.scale_)
        np.save(f"{path}_scaler_X_min.npy", self.scaler_X.min_)
        np.save(f"{path}_scaler_y.npy", self.scaler_y.scale_)
        np.save(f"{path}_scaler_y_min.npy", self.scaler_y.min_)

    def load(self, path):
        """
        Load the model and scalers.
        
        Args:
            path (str): Path to load the model from
        """
        self.model = models.load_model(f"{path}.h5", custom_objects={"GCNConv": GCNConv})

        self.scaler_X.scale_ = np.load(f"{path}_scaler_X.npy")
        self.scaler_X.min_ = np.load(f"{path}_scaler_X_min.npy")
        self.scaler_y.scale_ = np.load(f"{path}_scaler_y.npy")
        self.scaler_y.min_ = np.load(f"{path}_scaler_y_min.npy")
