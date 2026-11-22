with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re

tag_stack = []
for line_idx, line in enumerate(lines):
    # Find all html tags
    tokens = re.findall(r'<(/?[a-zA-Z0-9]+)[^>]*>', line)
    for t in tokens:
        tag = t.lower()
        if tag.startswith('/'):
            close_tag = tag[1:]
            if close_tag in ['input', 'img', 'br', 'hr', 'meta', 'link']:
                continue
            if tag_stack and tag_stack[-1][0] == close_tag:
                tag_stack.pop()
            else:
                # Mismatch!
                # print mismatch
                expected = tag_stack[-1][0] if tag_stack else 'NONE'
                # if line_idx between 1300 and 2300, print
                if 1300 <= line_idx <= 2400:
                    print(f"Line {line_idx+1}: unexpected closing tag </{close_tag}>, expected </{expected}> (stack depth {len(tag_stack)})")
                if tag_stack:
                    tag_stack.pop()
        else:
            open_tag = tag
            if open_tag in ['input', 'img', 'br', 'hr', 'meta', 'link']:
                continue
            tag_stack.append((open_tag, line_idx+1))

print(f"Final stack depth: {len(tag_stack)}")
