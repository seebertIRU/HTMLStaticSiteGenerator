import re
from enum import Enum

from htmlnode import LeafNode, ParentNode


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
    if not isinstance(text_node, TextNode):
        raise TypeError("text_node_to_html_node requires a TextNode instance.")

    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)

    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)

    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)

    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)

    if text_node.text_type == TextType.LINK:
        if text_node.url is None:
            raise ValueError("Link TextNodes require a URL.")
        return LeafNode("a", text_node.text, {"href": text_node.url})

    if text_node.text_type == TextType.IMAGE:
        if text_node.url is None:
            raise ValueError("Image TextNodes require a URL.")
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

    raise ValueError("Unsupported TextNode type.")


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        text = node.text
        images = extract_markdown_images(text)
        if not images:
            new_nodes.append(node)
            continue
        for alt, url in images:
            sections = text.split(f"![{alt}]({url})", 1)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            text = sections[1]
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        text = node.text
        links = extract_markdown_links(text)
        if not links:
            new_nodes.append(node)
            continue
        for link_text, url in links:
            sections = text.split(f"[{link_text}]({url})", 1)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            text = sections[1]
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        parts = node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown: unmatched delimiter '{delimiter}' in '{node.text}'")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))
    return new_nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split('\n\n')
    stripped = [block.strip() for block in blocks]
    return [block for block in stripped if block]


def block_to_block_type(block):
    lines = block.split('\n')
    if block.startswith('```') and block.endswith('```'):
        return BlockType.CODE
    if re.match(r'^#{1,6} ', block):
        return BlockType.HEADING
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    if all(line.startswith(f'{i+1}. ') for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def paragraph_to_html_node(block):
    text = block.replace('\n', ' ')
    children = text_to_children(text)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == '#':
            level += 1
        else:
            break
    if level < 1 or level > 6:
        raise ValueError("Invalid heading level")
    text = block[level:].strip().replace('\n', ' ')
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith('```') or not block.endswith('```'):
        raise ValueError("Invalid code block")
    content = block[3:-3].lstrip('\n')
    return ParentNode("pre", [LeafNode("code", content)])


def quote_to_html_node(block):
    lines = block.split('\n')
    stripped_lines = [line[1:].strip() if line.startswith('>') else line for line in lines]
    text = '\n'.join(stripped_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)


def ul_to_html_node(block):
    lines = block.split('\n')
    li_nodes = []
    for line in lines:
        if line.startswith('- '):
            text = line[2:].strip()
            children = text_to_children(text)
            li_nodes.append(ParentNode("li", children))
    return ParentNode("ul", li_nodes)


def ol_to_html_node(block):
    lines = block.split('\n')
    li_nodes = []
    for line in lines:
        parts = line.split('. ', 1)
        if len(parts) == 2:
            text = parts[1].strip()
            children = text_to_children(text)
            li_nodes.append(ParentNode("li", children))
    return ParentNode("ol", li_nodes)


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            children.append(paragraph_to_html_node(block))
        elif block_type == BlockType.HEADING:
            children.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            children.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(ul_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(ol_to_html_node(block))
    return ParentNode("div", children)
