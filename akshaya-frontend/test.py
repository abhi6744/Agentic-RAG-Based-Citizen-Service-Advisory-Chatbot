import re

with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the FlatList node
# We want to remove from <FlatList ... to the closing /> of FlatList
content = re.sub(r'<FlatList[\s\S]*?renderItem=\{.*?=>.*?\}\} \/>', '', content)
# Wait, it's easier to just find the entire block and remove it.
# Let's use string manipulation based on finding "<FlatList" and "/>" but that could match the main FlatList!
# The main list is also a FlatList! 
# Let's look for "data={filters}"
