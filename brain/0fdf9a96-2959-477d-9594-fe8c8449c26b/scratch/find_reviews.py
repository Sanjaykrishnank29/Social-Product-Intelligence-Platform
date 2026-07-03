from bs4 import BeautifulSoup
import os
import re

filepath = r"C:\Users\DELL\.gemini\antigravity-ide\brain\0fdf9a96-2959-477d-9594-fe8c8449c26b\.system_generated\steps\1113\content.md"

if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Let's extract script blocks and see if we can find JSON payloads
    # or search the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Print the text content of elements that contain reviews
    # Typically, reviews are in paragraphs (p) or spans or custom divs
    # Let's look for elements containing "return" or other terms
    print("Finding divs or spans containing 'return':")
    matches = soup.find_all(text=re.compile(r'return', re.IGNORECASE))
    print(f"Found {len(matches)} text matches")
    
    # Print first 10 unique non-empty text matches
    seen = set()
    count = 0
    for m in matches:
        t = m.strip()
        if t and len(t) > 10 and t not in seen:
            seen.add(t)
            print(f"[{count}]: {t[:200]}")
            count += 1
            if count >= 15:
                break
else:
    print("File not found")
