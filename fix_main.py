with open('core/main.py', 'rb') as f:
    content = f.read()

# Find and fix the garbled docstring
idx = content.find(b'Ctrl+S')
if idx != -1:
    print(f"Found at byte {idx}")
    print(content[idx:idx+50])
    # Find the end of the line
    end = content.find(b'\n', idx)
    print(f"Line: {content[idx:end]}")
    # Replace with correct UTF-8
    new_line = "        \"\"\"Ctrl+S 手动存档\"\"\"\n".encode('utf-8')
    content = content[:idx] + new_line + content[end+1:]
    with open('core/main.py', 'wb') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Not found")