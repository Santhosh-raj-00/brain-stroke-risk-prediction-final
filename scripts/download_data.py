import requests
import os

DATA_DIR = 'data'
FILE_PATH = os.path.join(DATA_DIR, 'stroke_data.csv')
URLS = [
    "https://raw.githubusercontent.com/fedesoriano/Stroke-Prediction-Dataset/master/healthcare-dataset-stroke-data.csv",
    "https://gist.githubusercontent.com/aiforsec/4b04d135e31505d69r6j/raw/healthcare-dataset-stroke-data.csv", 
    "https://raw.githubusercontent.com/jbrownlee/Datasets/master/stroke-data.csv",
    "https://raw.githubusercontent.com/augustwenty/predictions-stroke/master/healthcare-dataset-stroke-data.csv",
    "https://raw.githubusercontent.com/shashank-ne/Stroke-Prediction/master/Dataset/healthcare-dataset-stroke-data.csv",
    "https://raw.githubusercontent.com/naimrie/Stroke-Prediction-Dataset/master/healthcare-dataset-stroke-data.csv"
]

def download_file():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for url in URLS:
        print(f"Trying to download from {url}...")
        try:
            response = requests.get(url)
            if response.status_code == 200 and 'id,gender' in response.text: # Basic validation
                with open(FILE_PATH, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Successfully downloaded to {FILE_PATH}")
                return True
        except Exception as e:
            print(f"Failed: {e}")
            
    # If all fail, create a minimal REAL mock from the prompt spec (as a fallback) 
    # BUT the prompt says "REMOVE SYNTHETIC DATA".
    # I made a mistake in previous thought - I should NOT mock it. 
    # But if I can't simple download it, I'm stuck. 
    # I will try to use the raw text if I can find it in search.
    
    print("Could not download dataset.")
    return False

if __name__ == "__main__":
    download_file()
