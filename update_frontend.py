import os
import glob
import re

folder = 'd:/demo/demo/brain_stroke_prediction/frontend/src'
files = glob.glob(f'{folder}/**/*.js', recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace specific known pattern
    new_content = re.sub(
        r"process\.env\.REACT_APP_API_URL\s*\|\|\s*'http://localhost:5000'",
        "import.meta.env.VITE_API_BASE_URL",
        content
    )

    # In AuthContext.js
    new_content = re.sub(
        r"const apiUrl = process\.env\.REACT_APP_API_URL;",
        "const apiUrl = import.meta.env.VITE_API_BASE_URL;",
        new_content
    )

    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file}")
