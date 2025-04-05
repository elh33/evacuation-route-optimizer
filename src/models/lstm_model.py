"""LSTM model for time-series prediction of weather and traffic conditions."""
import os
import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from config import LSTM_PARAMS, PROCESSED_DATA_DIR, LSTM_MODEL_DIR

logger = logging.getLogger(__name__)

class WeatherTrafficLSTM:
    """LSTM model for predicting weather and traffic conditions."""
    
    def __init__(self, 
                 input_shape, 
                 output_shape,
                 units=LSTM_PARAMS["units"],
                 dropout=LSTM_PARAMS["dropout"],
                 recurrent_dropout=LSTM_PARAMS["recurrent_dropout"],
                 return_sequences=LSTM_PARAMS["return_sequences"],
                 activation=LSTM_PARAMS["activation"]):
        """
        Initialize the LSTM model.
        
        Args:
            input_shape (tuple): Shape of input data (time_steps, features)
            output_shape (int): Number of output features
            units (int): Number of LSTM units
            dropout (float): Dropout rate
            recurrent_dropout (float): Recurrent dropout rate
            return_sequences (bool): Whether to return the full sequence
            activation (str): Activation function
        """
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.units = units
        self.dropout = dropout
        self.recurrent_dropout = recurrent_dropout
        self.return_sequences = return_sequences
        self.activation = activation
        
        self.model = self._build_model()
        self.scaler_X = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
    
    def _build_model(self):
        """
        Build the LSTM model architecture.
        
        Returns:
            tensorflow.keras.Model: Compiled LSTM model
        """
        model = models.Sequential([
            layers.LSTM(
                units=self.units,
                return_sequences=True,
                dropout=self.dropout,
                recurrent_dropout=self.recurrent_dropout,
                activation=self.activation,
                input_shape=self.input_shape
            ),
            layers.LSTM(
                units=self.units // 2,
                return_sequences=False,
                dropout=self.dropout,
                recurrent_dropout=self.recurrent_dropout,
                activation=self.activation
            ),
            layers.Dense(self.units // 4, activation='relu'),
            layers.Dropout(self.dropout),
            layers.Dense(self.output_shape)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_sequences(self, data, time_steps):
        """
        Prepare input sequences for the LSTM model.
        
        Args:
            data (numpy.ndarray): Input data
            time_steps (int): Number of time steps
            
        Returns:
            tuple: X and y sequences
        """
        X, y = [], []
        for i in range(len(data) - time_steps):
            X.append(data[i:(i + time_steps), :])
            y.append(data[i + time_steps, :])
        return np.array(X), np.array(y)
    
    def train(self, X, y, epochs=100, batch_size=32, validation_split=0.2):
        """
        Train the LSTM model.
        
        Args:
            X (numpy.ndarray): Input features
            y (numpy.ndarray): Target values
            epochs (int): Number of training epochs
            batch_size (int): Batch size
            validation_split (float): Fraction of data to use for validation
            
        Returns:
            tensorflow.keras.callbacks.History: Training history
        """
        # Normalize data
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y)
        
        # Prepare sequences
        time_steps = self.input_shape[0]
        X_seq, y_seq = self.prepare_sequences(X_scaled, time_steps)
        
        # Split into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X_seq, y_seq, test_size=validation_split, random_state=42
        )
        
        # Callbacks
        early_stopping = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train the model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=[early_stopping],
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """
        Make predictions with the LSTM model.
        
        Args:
            X (numpy.ndarray): Input features
            
        Returns:
            numpy.ndarray: Predicted values
        """
        # Normalize input
        X_scaled = self.scaler_X.transform(X)
        
        # Reshape for LSTM input
        time_steps = self.input_shape[0]
        X_seq = X_scaled[-time_steps:].reshape(1, time_steps, X.shape[1])
        
        # Make prediction
        y_pred_scaled = self.model.predict(X_seq)
        
        # Inverse transform
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)
        
        return y_pred
    
    def save(self, path):
        """
        Save the model and scalers.
        
        Args:
            path (str): Path to save the model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(f"{path}.h5")
        
        # Save scalers
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
        self.model = models.load_model(f"{path}.h5")
        
        # Load scalers
        scale_X = np.load(f"{path}_scaler_X.npy")
        min_X = np.load(f"{path}_scaler_X_min.npy")
        self.scaler_X = MinMaxScaler()
        self.scaler_X.scale_ = scale_X
        self.scaler_X.min_ = min_X
        
        scale_y = np.load(f"{path}_scaler_y.npy")
        min_y = np.load(f"{path}_scaler_y_min.npy")
        self.scaler_y = MinMaxScaler()
        self.scaler_y.scale_ = scale_y
        self.scaler_y.min_ = min_y


def main():
    """Main function to train or predict with the LSTM model."""
    parser = argparse.ArgumentParser(description="Train or predict with LSTM model")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", action="store_true", help="Make predictions")
    parser.add_argument("--data_path", type=str, help="Path to the data directory")
    parser.add_argument("--model_path", type=str, help="Path to save/load the model")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    args = parser.parse_args()
    
    # Default paths
    if not args.data_path:
        args.data_path = PROCESSED_DATA_DIR / "weather"
    
    if not args.model_path:
        args.model_path = LSTM_MODEL_DIR / "weather_traffic_lstm"
    
    # Load data
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"Data directory {data_path} does not exist")
        return
    
    # Sample data loading - replace with your actual data loading logic
    try:
        # Assuming a CSV file with weather and traffic data
        data = pd.read_csv(data_path / "weather_traffic_data.csv")
        X = data.drop(columns=['timestamp']).values
        y = data.drop(columns=['timestamp']).values  # Same as X for demonstration
        
        # Define input shape based on data
        time_steps = 24  # Example: 24 hours of data
        features = X.shape[1]
        
        # Initialize the model
        model = WeatherTrafficLSTM(
            input_shape=(time_steps, features),
            output_shape=features
        )
        
        if args.train:
            logger.info("Training LSTM model...")
            history = model.train(
                X, y,
                epochs=args.epochs,
                batch_size=args.batch_size
            )
            logger.info(f"Training completed. Final loss: {history.history['loss'][-1]}")
            
            # Save the model
            model.save(args.model_path)
            logger.info(f"Model saved to {args.model_path}")
        
        elif args.predict:
            logger.info("Loading LSTM model for prediction...")
            model.load(args.model_path)
            
            # Make predictions
            predictions = model.predict(X[-time_steps-1:-1])
            logger.info(f"Prediction shape: {predictions.shape}")
            logger.info(f"Predictions: {predictions}")
        
        else:
            logger.warning("No action specified. Use --train or --predict")
    
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()