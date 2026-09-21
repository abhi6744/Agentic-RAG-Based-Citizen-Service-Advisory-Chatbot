import os
import re

for root, _, files in os.walk("src"):
    for file in files:
        if file.endswith(".ts") or file.endswith(".tsx"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple check if Platform is used but not imported
            if "Platform." in content and "Platform" not in content[:content.find("Platform.")]:
                print(f"Missing Platform in {path}")
            
            # Simple check for React hooks used but not imported
            for hook in ["useState", "useEffect", "useRef", "useMemo"]:
                if f"{hook}(" in content and f"import {{ {hook}" not in content and f"import {{{hook}" not in content and f"{hook}," not in content[:content.find(f"{hook}(")]:
                    # We might have `React.useState` which is fine.
                    if f"React.{hook}" not in content:
                        print(f"Missing {hook} in {path}")

