import unittest
from parameterized import parameterized

from split_msg import fragment_html

class TestErrorsHTMLFragmentation(unittest.TestCase):
    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_unclosed_tag(self, char_limit):
        html = "<div><p>Hello, world!"
        with self.assertRaises(Exception) as cm:
            fragment_html(html, char_limit)
        self.assertEqual(str(cm.exception), 'Invalid HTML structure')

    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_mismatched_tags(self, char_limit):
        html = "<div><p>Hello</div></p>"
        with self.assertRaises(Exception) as cm:
            fragment_html(html, char_limit)
        self.assertEqual(str(cm.exception), 'Invalid HTML structure')

    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_missing_closing_html(self, char_limit):
        html = "<html><body><div><p>Content</p>"
        with self.assertRaises(Exception) as cm:
            fragment_html(html, char_limit)
        self.assertEqual(str(cm.exception), 'Invalid HTML structure')
    
    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_invalid_nested_structure(self, char_limit):
        html = "<div><p><span>Text</div></span></p>"
        with self.assertRaises(Exception) as cm:
            fragment_html(html, char_limit)
        self.assertEqual(str(cm.exception), 'Invalid HTML structure')

    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_text_outside_tags(self, char_limit):
        html = "Hello<div><p>World</p></div>Ehlo"
        fragments = fragment_html(html, char_limit)
        # Ensure text outside tags is preserved
        total_text = "".join(
            frag.replace("<div>", "").replace("</div>", "").replace("<p>", "").replace("</p>", "")
            for frag in fragments
        )
        self.assertEqual(total_text, "HelloWorldEhlo")

    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_missing_opening_tags(self, char_limit):
        html = "Content</p></div>"
        with self.assertRaises(Exception) as cm:
            fragment_html(html, char_limit)
        self.assertEqual(str(cm.exception), 'Invalid HTML structure')

    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4096,), (4396,),
    ])
    def test_empty_html(self, char_limit):
        html = ""
        fragments = fragment_html(html, char_limit)
        # Ensure empty input results in no fragments
        self.assertEqual(fragments, [])

if __name__ == "__main__":
    unittest.main()