import re

with open('app/services/agentic_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "import logging" not in content:
    content = content.replace('import json', 'import json\nimport logging')

if "logger = logging.getLogger(__name__)" not in content:
    content = content.replace('settings = get_settings()', 'settings = get_settings()\nlogger = logging.getLogger(__name__)')

with open('app/services/agentic_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added logger to agentic_controller.py")
