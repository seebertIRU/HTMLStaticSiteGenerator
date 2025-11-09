import unittest
from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, BlockType, block_to_block_type, markdown_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("Different text", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_url_none_vs_value(self):
        node = TextNode("This is a text node", TextType.LINK, url=None)
        node2 = TextNode("This is a text node", TextType.LINK, url="https://example.com")
        self.assertNotEqual(node, node2)

    def test_eq_all_properties(self):
        node = TextNode("Click here", TextType.LINK, url="https://example.com")
        node2 = TextNode("Click here", TextType.LINK, url="https://example.com")
        self.assertEqual(node, node2)

    def test_split_nodes_delimiter_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_italic(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_unmatched_delimiter(self):
        node = TextNode("This is text with a `code block word", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_non_text_node(self):
        node1 = TextNode("This is text", TextType.TEXT)
        node2 = TextNode("Bold text", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        expected = [
            TextNode("This is text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_multiple_delimiters(self):
        node = TextNode("`code1` and `code2`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code1", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("code2", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_delimiter_at_start(self):
        node = TextNode("`code` at start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_delimiter_at_end(self):
        node = TextNode("at end `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("at end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_images_no_images(self):
        matches = extract_markdown_images("This is text with no images")
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(expected, matches)

    def test_extract_markdown_links_no_links(self):
        matches = extract_markdown_links("This is text with no links")
        self.assertListEqual([], matches)

    def test_extract_markdown_links_with_images(self):
        text = "This is text with a ![image](https://i.imgur.com/zjjcJKZ.png) and [link](https://example.com)"
        image_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], image_matches)
        self.assertListEqual([("link", "https://example.com")], link_matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_image_at_start(self):
        node = TextNode("![image](https://i.imgur.com/zjjcJKZ.png) at start", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_image_at_end(self):
        node = TextNode("at end ![image](https://i.imgur.com/zjjcJKZ.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("at end ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_non_text_node(self):
        node1 = TextNode("This is text", TextType.TEXT)
        node2 = TextNode("Bold text", TextType.BOLD)
        new_nodes = split_nodes_image([node1, node2])
        expected = [
            TextNode("This is text", TextType.TEXT),
            TextNode("Bold text", TextType.BOLD),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_link_at_start(self):
        node = TextNode("[link](https://example.com) at start", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_link_at_end(self):
        node = TextNode("at end [link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("at end ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_non_text_node(self):
        node1 = TextNode("This is text", TextType.TEXT)
        node2 = TextNode("Italic text", TextType.ITALIC)
        new_nodes = split_nodes_link([node1, node2])
        expected = [
            TextNode("This is text", TextType.TEXT),
            TextNode("Italic text", TextType.ITALIC),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_with_images(self):
        node = TextNode(
            "This is text with a ![image](https://i.imgur.com/zjjcJKZ.png) and [link](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        # Links should be split, images remain in text
        expected = [
            TextNode("This is text with a ![image](https://i.imgur.com/zjjcJKZ.png) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_plain_text(self):
        text = "This is plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_bold(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_image(self):
        text = "Here is an ![image](https://example.com/img.png)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Here is an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_mixed(self):
        text = "**Bold** and _italic_ with `code` ![img](url) [link](url)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url"),
            TextNode(" ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
        ]
        self.assertListEqual(expected, nodes)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type_paragraph(self):
        block = "This is a paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        block2 = "## This is a heading"
        self.assertEqual(block_to_block_type(block2), BlockType.HEADING)
        block3 = "###### This is a heading"
        self.assertEqual(block_to_block_type(block3), BlockType.HEADING)

    def test_block_to_block_type_code(self):
        block = "```python\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_quote(self):
        block = "> This is a quote\n> Another line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        block = "1. Item 1\n2. Item 2\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()


