import os

def contains_emoji(text):
    for char in text:
        # Check if character is in common emoji ranges
        # basic emoticons and symbols are often 1F600-1F64F, 1F300-1F5FF, 1F680-1F6FF, 1F900-1F9FF, etc.
        # But let's just look for anything above 0xFFFF or specific ranges
        cp = ord(char)
        if (0x1F600 <= cp <= 0x1F64F) or \
           (0x1F300 <= cp <= 0x1F5FF) or \
           (0x1F680 <= cp <= 0x1F6FF) or \
           (0x1F900 <= cp <= 0x1F9FF) or \
           (0x2600 <= cp <= 0x26FF) or \
           (0x2700 <= cp <= 0x27BF):
            return True
    return False

search_dir = "c:/Users/F3LX_STORE/Downloads/MetricsMonitoring/dashboard"
print(f"Scanning {search_dir} for emojis...")

for root, dirs, files in os.walk(search_dir):
    if "node_modules" in root or ".git" in root or ".next" in root:
        continue
    for file in files:
        if file.endswith((".tsx", ".ts", ".js", ".jsx", ".json", ".css")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    with open("found_emojis.txt", "a", encoding="utf-8") as out:
                        if contains_emoji(content):
                            out.write(f"Found emoji in {path}\n")
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if contains_emoji(line):
                                    out.write(f"  Line {i+1}: {line.strip()[:100]}\n")
            except Exception as e:
                pass
