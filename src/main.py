import os
import shutil
from textnode import markdown_to_html_node


def copy_files_recursive(source, destination):
    if os.path.exists(destination):
        shutil.rmtree(destination)
    
    os.mkdir(destination)
    
    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)
        
        if os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)
            print(f"Copied file: {source_path}")
        else:
            copy_files_recursive(source_path, destination_path)


def extract_title(markdown):
    lines = markdown.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    raise Exception("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    with open(from_path, 'r') as f:
        markdown_content = f.read()
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    title = extract_title(markdown_content)
    
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    with open(dest_path, 'w') as f:
        f.write(full_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item)
        
        if os.path.isfile(item_path):
            if item.endswith('.md'):
                dest_html_path = dest_path.replace('.md', '.html')
                generate_page(item_path, template_path, dest_html_path)
        else:
            generate_pages_recursive(item_path, template_path, dest_path)


def main():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(script_dir)
    
    copy_files_recursive("static", "public")
    generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()
