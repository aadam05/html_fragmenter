import unittest
from parameterized import parameterized

from split_msg import fragment_html

class TestSimpleHTMLFragmentation(unittest.TestCase):
    @parameterized.expand([
        (50,), (100,), (200,),
        (2000,), (2500,), (3600,),
        (3990,), (4096,), (4396,),
    ])
    def test_simple_html(self, char_limit):
        html = "<div><p>Hello, world!</p></div>"
        fragments = fragment_html(html, char_limit)
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0], "<div><p>Hello, world!</p></div>")

    @parameterized.expand([
        (50, 558), (50, 600),
        (100, 558), (100, 600),
        (2500, 9000), (3500, 9000),
        (4096, 9000), (4396, 9000),
    ])
    def test_long_text_split(self, char_limit, text_len):
        html = "<p>" + "A" * text_len + "</p>"
        fragments = fragment_html(html, char_limit)
        min_fragment_len = len(html) // char_limit
        self.assertGreaterEqual(len(fragments), min_fragment_len)  # Ensure multiple fragments are created
        total_text = "".join(frag.strip("<p></p>") for frag in fragments)  # Recombine text
        self.assertEqual(total_text, "A" * text_len)  # Ensure no data is lost
    
    @parameterized.expand([
        (50,), (100,), (200,),
        (3990,), (4396,), (4396,),
    ])
    def test_single_long_text_node(self, char_limit):
        html = "A" * 300
        fragments = fragment_html(html, char_limit)
        total_text = "".join(frag for frag in fragments)
        self.assertEqual(total_text, "A" * 300)  # Verify that no characters are lost
        for frag in fragments:
            self.assertLessEqual(len(frag), char_limit)  # Ensure each fragment is within limit

if __name__ == "__main__":
    unittest.main()
