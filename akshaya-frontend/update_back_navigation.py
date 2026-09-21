import re
import glob

files = glob.glob('src/app/*.tsx')

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "router.back()" in content:
        content = content.replace('router.back()', "router.canGoBack() ? router.back() : router.replace('/')")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
