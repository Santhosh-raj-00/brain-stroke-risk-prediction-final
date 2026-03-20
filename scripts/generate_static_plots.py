
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.train_model import StrokePredictionModel

def generate_static_plots():
    print("Generating static model visualizations...")
    output_dir = 'static/images'
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize model to generate data
    model = StrokePredictionModel()
    
    # 1. Generate Data
    print("Generating synthetic data...")
    df = model._generate_realistic_synthetic_data(n_samples=5000)
    
    # 2. Correlation Heatmap
    print("Generating Correlation Heatmap...")
    plt.figure(figsize=(12, 10))
    # Select numeric columns for correlation
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    
    sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0, fmt='.2f')
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'), dpi=100)
    plt.close()
    
    # 3. Confusion Matrix (Need trained model predictions)
    # We load the trained model to get real performance on this new synthetic set
    try:
        model.load_model()
        X, y = model._preprocess_training_data(df)
        
        # Predict
        y_pred = model.model.predict(X)
        
        print("Generating Confusion Matrix...")
        cm = confusion_matrix(y, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['No Stroke', 'Stroke'],
                   yticklabels=['No Stroke', 'Stroke'])
        plt.title('Model Confusion Matrix (Validation Set)')
        plt.ylabel('Actual Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=100)
        plt.close()
        
    except Exception as e:
        print(f"Could not generate confusion matrix: {e}")
        # Create a placeholder if model fails
        plt.figure(figsize=(6, 6))
        plt.text(0.5, 0.5, "Model Data Unavailable", ha='center')
        plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
        plt.close()

    print(f"Static plots saved to {output_dir}")

if __name__ == '__main__':
    generate_static_plots()
