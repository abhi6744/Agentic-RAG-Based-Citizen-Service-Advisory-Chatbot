with open('akshaya-frontend/src/app/index.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if '{/* Summary */}' in line:
        skip = True
    if skip and '{/* Documents & Eligibility */}' in line:
        skip = False
    
    if not skip:
        new_lines.append(line)

with open('akshaya-frontend/src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
