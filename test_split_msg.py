import unittest
from parameterized import parameterized

from split_msg import fragment_html


class TestFragmentHTML(unittest.TestCase):
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
        ('./test1.html', 900), ('./test2.html', 150), ('./test3.html', 150), ('./test4.html', 150),
        ('./test1.html', 1000), ('./test2.html', 1000), ('./test3.html', 1500), ('./test4.html', 2500),
        ('./test1.html', 3990), ('./test2.html', 3990), ('./test3.html', 4096), ('./test4.html', 4396),
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
