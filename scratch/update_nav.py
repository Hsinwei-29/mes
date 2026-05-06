import os
import glob

directory = 'app/views/templates/main'

for filepath in glob.glob(os.path.join(directory, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nav block variations exist, but they usually look like:
    # <nav class="main-nav">
    #     <a href="{{ url_for('main.index') }}" ...>庫存看板</a>
    #     <a href="{{ url_for('main.orders_page') }}" ...>工單需求</a>
    #     <a href="{{ url_for('main.shortage_page') }}" ...>缺料分析</a>
    #     <a href="{{ url_for('main.lifting_page') }}" ...>吊具管理</a>
    # </nav>
    # We want to replace the orders and shortage links to be wrapped in if block
    # Note: index.html already done.
    if 'index.html' in filepath:
        continue

    # We will look for lines containing `main.orders_page` and `main.shortage_page`
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'main.orders_page' in line and not '{% if' in lines[i-1]:
            # we found orders_page, we should wrap it and shortage page
            # find indentation
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + '{% if current_user.is_authenticated and current_user.is_admin() %}')
            new_lines.append(line)
            
            # Check next line if it is shortage_page
            if i + 1 < len(lines) and 'main.shortage_page' in lines[i+1]:
                new_lines.append(lines[i+1])
                i += 1
            new_lines.append(indent + '{% endif %}')
        elif 'main.shortage_page' in line and not ('{% if' in lines[i-2] or '{% if' in lines[i-1]):
            # Fallback if only shortage is found, or it wasn't caught by the above
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + '{% if current_user.is_authenticated and current_user.is_admin() %}')
            new_lines.append(line)
            new_lines.append(indent + '{% endif %}')
        else:
            new_lines.append(line)
        i += 1
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f"Updated {filepath}")
