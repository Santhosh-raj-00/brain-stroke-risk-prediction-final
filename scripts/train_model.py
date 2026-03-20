
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrokeRiskModel:
    def __init__(self, model_dir='ml_models', data_path='data/stroke_data.csv'):
        self.model_dir = model_dir
        self.data_path = data_path
        self.model_path = os.path.join(model_dir, 'xgboost_stroke.pkl')
        self.scaler_path = os.path.join(model_dir, 'scaler.pkl')
        self.imputer_path = os.path.join(model_dir, 'imputer.pkl')
        self.encoders_path = os.path.join(model_dir, 'encoders.pkl')
        self.config_path = os.path.join(model_dir, 'model_config.json')
        
        self.model = None
        self.scaler = None
        self.imputer = None
        self.encoders = {}
        self.feature_columns = None
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

    def load_data(self):
        """Load real clinical data from CSV"""
        if not os.path.exists(self.data_path):
            error_msg = f"""
            CRITICAL ERROR: Real dataset not found at {self.data_path}
            
            You must download the 'healthcare-dataset-stroke-data.csv' (Kaggle Stroke Prediction Dataset)
            and place it in the 'data' folder.
            
            Download Link: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
            """
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded dataset with {len(df)} records")
        return df

    def preprocess_data(self, df):
        """Preprocess data: Handle missing values, encode cat variables, scale"""
        # Drop ID if exists
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
            
        # Handle Missing Values
        # BMI is often missing
        if self.imputer is None:
            self.imputer = SimpleImputer(strategy='mean')
            df['bmi'] = self.imputer.fit_transform(df[['bmi']]).flatten()
        else:
            df['bmi'] = self.imputer.transform(df[['bmi']]).flatten()
            
        # Separate features and target
        if 'stroke' in df.columns:
            y = df['stroke']
            X = df.drop('stroke', axis=1)
        else:
            y = None
            X = df
            
        # Encoding Categorical Variables
        categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
        
        # Verify columns exist
        for col in categorical_cols:
            if col not in X.columns:
                # Add missing columns with default 'Unknown' or mode if predicting
                X[col] = 'Unknown'

        # Use One-Hot Encoding for training (simpler for feature importance than LabelEncoder)
        # But for saving/loading consistency, we need to ensure columns match.
        # Let's use get_dummies but align with saved columns.
        
        X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
        
        # Normalize/Scale Numerical Features
        numerical_cols = ['age', 'avg_glucose_level', 'bmi']
        # Note: Hypertension and Heart Disease are already 0/1, treating as numeric or cat is fine. 
        # Usually they are left as is or scaled. Let's scale them too for uniformity with some models, 
        # but for XGBoost it doesn't matter much. Let's only scale continuous.
        
        if self.scaler is None:
            self.scaler = StandardScaler()
            X_encoded[numerical_cols] = self.scaler.fit_transform(X_encoded[numerical_cols])
        else:
            X_encoded[numerical_cols] = self.scaler.transform(X_encoded[numerical_cols])
            
        # Store feature columns to ensure consistency during prediction
        if self.feature_columns is None:
            self.feature_columns = X_encoded.columns.tolist()
        else:
            # Add missing columns (seen in train, not in test)
            for col in self.feature_columns:
                if col not in X_encoded.columns:
                    X_encoded[col] = 0
            # Reorder
            X_encoded = X_encoded[self.feature_columns]
            
        return X_encoded, y

    def train(self):
        """Train the model using Real Data"""
        print("="*60)
        print("TRAINING MODEL ON REAL CLINICAL DATA")
        print("="*60)
        
        df = self.load_data()
        
        # Preprocess
        X, y = self.preprocess_data(df)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train XGBoost
        # Calculate scale_pos_weight for imbalance
        pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)
        
        self.model = XGBClassifier(
            scale_pos_weight=pos_weight,
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        print("\nModel Evaluation:")
        print(classification_report(y_test, y_pred))
        print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")
        
        # Save artifacts
        self.save_model()
        
    def save_model(self):
        """Save all model artifacts"""
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.imputer, self.imputer_path)
        
        config = {
            'feature_columns': self.feature_columns,
            'model_version': '3.0.0-REAL',
            'timestamp': pd.Timestamp.now().isoformat()
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
            
        logger.info(f"Model saved to {self.model_dir}")

    def load_model(self):
        """Load model artifacts"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError("Model not found. Please train it first.")
            
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.imputer = joblib.load(self.imputer_path)
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.feature_columns = config['feature_columns']

    def predict(self, input_data):
        """
        Predict stroke risk for a single patient
        input_data: dict of values
        """
        if self.model is None:
            self.load_model()
            
        # Convert dict to DF
        df = pd.DataFrame([input_data])
        
        # Preprocess using saved artifacts
        X, _ = self.preprocess_data(df)
        
        # Predict
        prob = self.model.predict_proba(X)[0, 1]
        
        # Risk Class (User defined)
        # Low 0-20%, Medium 21-60%, High 61-100%
        if prob <= 0.20:
            risk_class = 'Low'
        elif prob <= 0.60:
            risk_class = 'Medium'
        else:
            risk_class = 'High'
            
        return prob, risk_class

if __name__ == "__main__":
    try:
        model = StrokeRiskModel()
        model.train()
    except Exception as e:
        cleaned_msg = str(e).replace('CRITICAL ERROR:', '').strip()
        print(f"\n[ERROR] TRAINING FAILED: {cleaned_msg}\n")
