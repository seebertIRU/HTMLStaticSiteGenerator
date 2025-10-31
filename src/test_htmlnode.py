import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_single(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com" target="_blank"')

    def test_props_to_html_empty(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.props_to_html(), '')

    def test_repr(self):
        node = HTMLNode(tag="p", value="Hello", props={"class": "text"})
        expected = "HTMLNode(tag='p', value='Hello', children=[], props={'class': 'text'})"
        self.assertEqual(repr(node), expected)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_text(self):
        node = LeafNode(None, "Plain text")
        self.assertEqual(node.to_html(), "Plain text")

    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_value_required(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)


class TestParentNode(unittest.TestCase):
    def test_parent_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_parent_to_html_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "span",
                    [LeafNode(None, "Nested text")],
                )
            ],
        )
        self.assertEqual(node.to_html(), "<div><span>Nested text</span></div>")

    def test_parent_to_html_with_props(self):
        node = ParentNode(
            "ul",
            [LeafNode("li", "Item 1"), LeafNode("li", "Item 2")],
            {"class": "list"},
        )
        self.assertEqual(
            node.to_html(),
            '<ul class="list"><li>Item 1</li><li>Item 2</li></ul>',
        )

    def test_parent_requires_tag(self):
        with self.assertRaises(ValueError):
            ParentNode(None, [LeafNode(None, "Text")])

    def test_parent_requires_children_missing(self):
        with self.assertRaises(ValueError):
            ParentNode("p", None)

    def test_parent_requires_children_non_empty(self):
        with self.assertRaises(ValueError):
            ParentNode("p", [])

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code(self):
        node = TextNode("print('hello')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hello')")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props.get("href"), "https://example.com")

    def test_link_missing_url(self):
        node = TextNode("Click here", TextType.LINK)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props.get("src"), "https://example.com/image.png")
        self.assertEqual(html_node.props.get("alt"), "Alt text")

    def test_image_missing_url(self):
        node = TextNode("Alt text", TextType.IMAGE)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_unknown_type(self):
        node = TextNode("Unknown", "unknown")
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()
