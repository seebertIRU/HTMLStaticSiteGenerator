import unittest
from main import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_simple(self):
        markdown = "# Hello"
        self.assertEqual(extract_title(markdown), "Hello")
    
    def test_extract_title_with_content(self):
        markdown = "# My Title\n\nSome content here"
        self.assertEqual(extract_title(markdown), "My Title")
    
    def test_extract_title_with_whitespace(self):
        markdown = "#   Spaced Title   \n\nContent"
        self.assertEqual(extract_title(markdown), "Spaced Title")
    
    def test_extract_title_not_at_start(self):
        markdown = "Some text\n# Later Title\n\nMore content"
        self.assertEqual(extract_title(markdown), "Later Title")
    
    def test_extract_title_no_h1(self):
        markdown = "## H2 Header\n\n### H3 Header\n\nNo h1 here"
        with self.assertRaises(Exception):
            extract_title(markdown)
    
    def test_extract_title_no_header(self):
        markdown = "Just some plain text\nWith no headers"
        with self.assertRaises(Exception):
            extract_title(markdown)
    
    def test_extract_title_multiple_h1(self):
        markdown = "# First Title\n\nContent\n\n# Second Title"
        self.assertEqual(extract_title(markdown), "First Title")


if __name__ == "__main__":
    unittest.main()
