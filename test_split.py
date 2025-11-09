from src.textnode import TextNode, TextType, split_nodes_delimiter

# Test basic
node = TextNode("This is text with a `code block` word", TextType.TEXT)
new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
print("Test 1:", new_nodes)

# Test unmatched
try:
    node2 = TextNode("This is text with a `code block word", TextType.TEXT)
    split_nodes_delimiter([node2], "`", TextType.CODE)
except ValueError as e:
    print("Test 2: Error as expected:", e)

# Test no delimiter
node3 = TextNode("Plain text", TextType.TEXT)
new_nodes3 = split_nodes_delimiter([node3], "`", TextType.CODE)
print("Test 3:", new_nodes3)