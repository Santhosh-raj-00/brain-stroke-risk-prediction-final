import pandas as pd
import numpy as np
import joblib
import json
from typing import Dict, Any, Tuple, List
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

try:
    from xgboost import XGBClassifier
except ImportError:
    print("XGBoost not found. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "xgboost"])
    from xgboost import XGBClassifier


class StrokeRiskMLService:
    def __init__(self, model_path: str = '../ml_models/xgboost_stroke.pkl', 
                 schema_path: str = '../ml_models/feature_schema.json'):
        """
        Initialize the Stroke Risk ML Service
        
        Args:
            model_path: Path to the trained XGBoost model
            schema_path: Path to the feature schema
        """
        self.model_path = model_path
        self.schema_path = schema_path
        self.model = None
        self.feature_schema = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = None
        
        # Load model and schema
        self.load_model()
        self.load_feature_schema()
    
    def load_model(self):
        """Load the trained XGBoost model safely for production"""
        try:
            if not os.path.exists(self.model_path):
                print(f"Model loading error: Model file not found at {self.model_path}.")
            else:
                self.model = joblib.load(self.model_path)
                print("Model loaded successfully.")
                
                # Initialize SHAP explainer
                import shap
                try:
                    self.explainer = shap.TreeExplainer(self.model)
                    print("SHAP explainer initialized.")
                except Exception as e:
                    print(f"SHAP explainer initialization error: {e}")
        except Exception as e:
            print(f"Model loading error: {e}")
    
    def _train_model(self):
        """Train a proper XGBoost model with synthetic data"""
        print("Training a new XGBoost model for stroke risk prediction...")
        
        # Create synthetic training data based on medical knowledge
        np.random.seed(42)
        n_samples = 5000
        
        # Generate synthetic patient data
        age = np.random.normal(50, 20, n_samples)
        age = np.clip(age, 18, 100)
        
        hypertension = np.random.binomial(1, 0.3, n_samples)  # 30% prevalence
        heart_disease = np.random.binomial(1, 0.15, n_samples)  # 15% prevalence
        
        # Glucose levels (higher in diabetics)
        avg_glucose_level = np.random.normal(100, 30, n_samples)
        avg_glucose_level = np.clip(avg_glucose_level, 50, 300)
        # Increase glucose for people with heart disease or hypertension
        avg_glucose_level += heart_disease * 20 + hypertension * 15
        
        # BMI (higher values increase stroke risk)
        bmi = np.random.normal(25, 5, n_samples)
        bmi = np.clip(bmi, 15, 50)
        
        # Gender (male slightly higher risk)
        gender = np.random.choice(['Male', 'Female', 'Other'], n_samples, p=[0.5, 0.48, 0.02])
        
        # Marital status (married slightly protective)
        ever_married = np.random.choice(['Yes', 'No'], n_samples, p=[0.7, 0.3])
        
        # Work type (sedentary jobs slightly higher risk)
        work_type = np.random.choice([
            'Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'
        ], n_samples, p=[0.4, 0.15, 0.15, 0.15, 0.15])
        
        # Residence type
        residence_type = np.random.choice(['Urban', 'Rural'], n_samples, p=[0.6, 0.4])
        
        # Smoking status
        smoking_status = np.random.choice([
            'never smoked', 'smokes', 'formerly smoked', 'Unknown'
        ], n_samples, p=[0.5, 0.2, 0.2, 0.1])
        
        # Create synthetic target based on medical risk factors
        # Higher risk for older age, hypertension, heart disease, high glucose, high BMI
        stroke_risk_score = (
            (age - 40) / 100 +  # Age factor
            hypertension * 0.3 +  # Hypertension factor
            heart_disease * 0.25 +  # Heart disease factor
            (avg_glucose_level - 100) / 500 +  # Glucose factor
            (bmi - 20) / 100 +  # BMI factor
            np.where(gender == 'Male', 0.05, 0)  # Gender factor
        )
        
        # Add noise and convert to probability
        stroke_risk_score = np.clip(stroke_risk_score + np.random.normal(0, 0.1, n_samples), 0, 1)
        
        # Convert to binary outcome with some randomness
        stroke_target = (stroke_risk_score > np.percentile(stroke_risk_score, 85)).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'age': age,
            'hypertension': hypertension,
            'heart_disease': heart_disease,
            'avg_glucose_level': avg_glucose_level,
            'bmi': bmi,
            'gender': gender,
            'ever_married': ever_married,
            'work_type': work_type,
            'Residence_type': residence_type,
            'smoking_status': smoking_status,
            'stroke': stroke_target
        })
        
        # Preprocess the data
        X, y = self._preprocess_training_data(df)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train XGBoost model with class balancing
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=np.sum(y_train == 0) / np.sum(y_train == 1),  # Handle class imbalance
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_pred_proba)
        print(f"Trained model with AUC score: {auc_score:.3f}")
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
        
        # Also save to the correct location for the app
        correct_path = '../ml_models/xgboost_stroke.pkl'
        os.makedirs(os.path.dirname(correct_path), exist_ok=True)
        joblib.dump(self.model, correct_path)
        print(f"Model also saved to {correct_path}")
    
    def _preprocess_training_data(self, df):
        """Preprocess training data"""
        # Handle categorical variables with one-hot encoding
        categorical_columns = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
        
        # One-hot encode categorical features
        df_encoded = pd.get_dummies(df, columns=categorical_columns, prefix=categorical_columns, drop_first=True)
        
        # Separate features and target
        X = df_encoded.drop('stroke', axis=1)
        y = df_encoded['stroke']
        
        # Store feature column names for later use
        self.feature_columns = X.columns.tolist()
        
        # Scale numerical features
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
        
        return X_scaled, y
    
    def load_feature_schema(self):
        """Load the feature schema"""
        try:
            with open(self.schema_path, 'r') as f:
                self.feature_schema = json.load(f)
        except Exception as e:
            print(f"Error loading feature schema: {e}")
            # Create a basic schema as fallback
            self.feature_schema = {
                "features": [
                    "age", "hypertension", "heart_disease", 
                    "avg_glucose_level", "bmi", "gender_Male", "gender_Other"
                ],
                "categorical_columns": ["gender"],
                "numerical_columns": ["age", "hypertension", "heart_disease", "avg_glucose_level", "bmi"]
            }
    
    def preprocess_input(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocess input data to match the model's expected format
        
        Args:
            input_data: Raw input data from the API
            
        Returns:
            DataFrame with properly formatted features
        """
        # Create a dataframe with the input
        df = pd.DataFrame([input_data])
        
        # Ensure all categorical columns exist
        categorical_columns = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
        
        # One-hot encode categorical features
        df_encoded = df.copy()
        for col in categorical_columns:
            if col in df_encoded.columns:
                # Get all possible categories from schema or use default
                if col == 'gender':
                    possible_categories = ['Male', 'Female', 'Other']
                elif col == 'ever_married':
                    possible_categories = ['Yes', 'No']
                elif col == 'work_type':
                    possible_categories = ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked']
                elif col == 'Residence_type':
                    possible_categories = ['Urban', 'Rural']
                elif col == 'smoking_status':
                    possible_categories = ['never smoked', 'smokes', 'formerly smoked', 'Unknown']
                
                # Create one-hot encoded columns
                for category in possible_categories:
                    if category != 'Female':  # Use Female as baseline (drop first)
                        col_name = f"{col}_{category}" if category != 'Yes' and category != 'No' else f"{col}_{category}"
                        df_encoded[col_name] = (df_encoded[col] == category).astype(int)
                
                # Drop the original categorical column
                df_encoded = df_encoded.drop(columns=[col])
        
        # Ensure all expected features exist and are in the right order
        if self.feature_columns:
            for col in self.feature_columns:
                if col not in df_encoded.columns:
                    df_encoded[col] = 0  # Add missing features with default value
            
            # Reorder columns to match training
            df_encoded = df_encoded[self.feature_columns]
        else:
            # Fallback: use the columns that exist
            self.feature_columns = df_encoded.columns.tolist()
        
        # Scale the features
        df_scaled = pd.DataFrame(
            self.scaler.transform(df_encoded),
            columns=df_encoded.columns
        )
        
        return df_scaled
    
    def predict(self, input_data: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Make a prediction using the trained model
        
        Args:
            input_data: Input features for prediction
            
        Returns:
            Tuple of (risk_probability, feature_contributions)
        """
        try:
            # Preprocess the input
            processed_data = self.preprocess_input(input_data)
            
            # Make prediction using predict_proba to get actual probability
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(processed_data)
                # Get probability of positive class (stroke)
                risk_probability = probabilities[0][1]
                
                print(f"ML Probability: {risk_probability:.3f}")
            else:
                # Fallback for other models
                risk_probability = 0.5
            
            # Calculate feature contributions (SHAP values would go here)
            feature_contributions = self._calculate_feature_contributions(processed_data)
            
            print(f"Final Probability: {risk_probability:.3f}")
            
            return risk_probability, feature_contributions
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            # Return a default prediction in case of error
            risk_probability = 0.5
            print(f"Error - Default Probability: {risk_probability:.3f}")
            return risk_probability, {}

    def _calculate_feature_contributions(self, processed_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate feature contributions using SHAP values
        
        Args:
            processed_data: Preprocessed input data
            
        Returns:
            Dictionary of feature contributions
        """
        try:
            if hasattr(self, 'explainer'):
                shap_values = self.explainer.shap_values(processed_data)
                feature_names = processed_data.columns.tolist()
                
                contributions = {}
                for i, feature in enumerate(feature_names):
                    if isinstance(shap_values, list):
                        val = float(shap_values[1][0][i])
                    else:
                        val = float(shap_values[0][i])
                    contributions[feature] = val
                
                return contributions
        except Exception as e:
            print(f"Error calculating SHAP values: {e}")

        # Fallback to simple feature importance
        if hasattr(self.model, 'feature_importances_') and len(self.model.feature_importances_) == len(processed_data.columns):
            importances = self.model.feature_importances_
            feature_names = processed_data.columns.tolist()
            
            contributions = {}
            for i, feature in enumerate(feature_names):
                contribution = processed_data.iloc[0, i] * importances[i]
                contributions[feature] = float(contribution)
            
            return contributions
        else:
            feature_names = processed_data.columns.tolist()
            return {feature: 0.0 for feature in feature_names}
    
    def categorize_risk(self, risk_probability: float) -> str:
        """
        Categorize risk based on probability using medical guidelines
        
        Args:
            risk_probability: Risk probability score
            
        Returns:
            Risk category (LOW, MEDIUM, HIGH)
        """
        print(f"Risk categorization - Probability: {risk_probability:.3f}")
        
        # 0-20%: LOW, 21-60%: MEDIUM, 61-100%: HIGH
        if risk_probability <= 0.20:
            risk_level = 'LOW'
        elif risk_probability <= 0.60:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'
        
        print(f"Risk Level: {risk_level}")
        return risk_level


# Global instance for use in the app
ml_service = StrokeRiskMLService()