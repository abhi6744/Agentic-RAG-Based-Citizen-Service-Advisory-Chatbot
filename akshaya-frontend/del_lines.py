with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Delete lines 252 to 318 (0-indexed 251 to 317)
del lines[251:318]

with open('src/app/history.tsx', 'w', encoding='utf-8') as f:
    f.writelines(lines)
