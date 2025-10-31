import unittest
from textnode import TextNode, TextType

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

if __name__ == "__main__":
    unittest.main()


