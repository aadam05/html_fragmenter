import unittest
from parameterized import parameterized

from split_msg import fragment_html

html_examples_paths = [
    'html_examples/test1.html',
    'html_examples/test2.html',
    'html_examples/test3.html',
    'html_examples/test4.html'
]

class TestComplexHTMLFragmentation(unittest.TestCase):
    @parameterized.expand([
        (50, 80), (50, 150),
        (100, 80), (100, 150),
        (150, 300), (150, 550),
        (3500, 8000), (3990, 8000),
        (4096, 8000), (4396, 8000),
    ])
    def test_nested_tags(self, char_limit, text_len):
        html = "<div><p>" + "A" * text_len + "</p><p>" + "B" * (text_len // 2) + "</p></div>"
        fragments = fragment_html(html, char_limit)
        total_text = "".join(
            frag.replace("<div><p>", "").replace("</p></div>", "").replace("</p><p>", "")
            for frag in fragments
        )
        self.assertEqual(total_text, "A" * text_len + "B" * (text_len // 2))  # Ensure text integrity
    
    @parameterized.expand([
        (html_examples_paths[0], 900), (html_examples_paths[1], 150), (html_examples_paths[2], 150), (html_examples_paths[3], 150),
        (html_examples_paths[0], 1000), (html_examples_paths[1], 1000), (html_examples_paths[2], 1500), (html_examples_paths[3], 2500),
        (html_examples_paths[0], 3990), (html_examples_paths[1], 3990), (html_examples_paths[2], 4096), (html_examples_paths[3], 4396),
    ])
    def test_complex_html(self, html_source, char_limit):
        with open(html_source, 'r', encoding='utf-8') as file:
            html = file.read()
        fragments = fragment_html(html, char_limit)
        min_fragment_len = len(html) // char_limit
        self.assertGreaterEqual(len(fragments), min_fragment_len)  # Ensure multiple fragments are created
        for frag in fragments:
            self.assertLessEqual(len(frag), char_limit)  # Ensure each fragment is within limit
    
    @parameterized.expand([
        (50,), (100,), (150,),
        (3990,), (4396,), (4396,),
    ])
    def test_mixed_text_and_tags(self, char_limit):
        html = (
            "<div>"
            + "A" * 50
            + "<p>"
            + "B" * 200
            + "</p>"
            + "<a>"
            + "C" * 150
            + "</a>"
            + "</div>"
        )
        fragments = fragment_html(html, char_limit)
        total_text = "".join(
            frag.replace("<div>", "")
            .replace("</div>", "")
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("<a>", "")
            .replace("</a>", "")
            for frag in fragments
        )
        self.assertEqual(total_text, "A" * 50 + "B" * 200 + "C" * 150)
        for frag in fragments:
            self.assertLessEqual(len(frag), char_limit)  # Ensure limit compliance

if __name__ == "__main__":
    unittest.main()
