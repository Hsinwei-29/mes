import os
import glob

directory = 'app/views/templates/main'

for filepath in glob.glob(os.path.join(directory, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content.replace("app.js') }}?v=20260402_1105", "app.js') }}?v=20260504_1500")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated cache buster in {filepath}")
