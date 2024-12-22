import re
import sys
from typing import List, Tuple
from html.parser import HTMLParser
from collections.abc import Generator

# Default configuration values
html_example = './html_examples/example.html'

# Check command-line arguments for max length and source file
if len(sys.argv) > 1 and sys.argv[1].startswith('--max-len'):
    MAX_LEN = int(sys.argv[1].split('=')[1])
else:
    MAX_LEN = 4096

if len(sys.argv) > 2 and sys.argv[2].endswith('.html'):
    SOURCE_FILE = sys.argv[2]
else:
    SOURCE_FILE = html_example

class TagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tokens = []

    def handle_starttag(self, tag, attrs):
        attr_str = " ".join(f'{key}="{value}"' for key, value in attrs)
        res = f"<{tag} {attr_str}>".strip() if attrs else f'<{tag}>'
        self.tokens.append(res)

    def handle_endtag(self, tag):
        self.tokens.append(f"</{tag}>")

    def handle_data(self, data):
        if data.strip():
            self.tokens.append(data)

def fragment_html(html, char_limit=MAX_LEN) -> Generator[str]:
    parser = TagParser()
    parser.feed(html)
    tokens = parser.tokens

    fragments = []
    current_fragment = []
    char_count = 0
    open_tags: List[Tuple[str, str]] = []

    def close_open_tags():
        return "".join(f"</{tag}>" for tag, attr in reversed(open_tags))

    def reopen_tags():
        return "".join(f"<{tag} {attr}>" if attr else f"<{tag}>" for tag, attr in open_tags)

    def split_text_node(text: str, free_space_for_curr_token: int, free_space_for_next_tokens: int):
        """Split long text nodes into smaller chunks."""
        text_chunk_for_curr_token = text[0:free_space_for_curr_token]
        text = text[free_space_for_curr_token:]
        text_chunks = [text[i:i + free_space_for_next_tokens] for i in range(0, len(text), free_space_for_next_tokens)]
        return text_chunk_for_curr_token, text_chunks

    def calculate_total_block_size(char_count: int, token: str):
        """Estimate the size of a current fragment with token, including any closing tags."""
        if token.startswith("<") and not token.startswith("</"):  # start tag
            tag = re.match(r"<(\w+)", token).group(1)
            return char_count + len(token) + len(f"</{tag}>") + len(close_open_tags())
        elif token.startswith("</"):  # end tag
            return None
        else:  # text node
            return char_count + len(token) + len(close_open_tags())

    for token in tokens:
        if token.startswith("<") and not token.startswith("</"):  # start tag
            tag, attrs = re.match(r"<(\w+)(.*?)>", token).group(1, 2)
            total_block_size = calculate_total_block_size(char_count, token)
            if total_block_size > char_limit:
                current_fragment.append(close_open_tags())
                fragments.append("".join(current_fragment))

                if len(reopen_tags()) + len(token) + len(close_open_tags()) > char_limit:
                    raise ValueError("Either you set a small limit, or the HTML is too deep.")

                current_fragment = [reopen_tags()]
                char_count = len(reopen_tags())

            current_fragment.append(token)
            open_tags.append(
                (tag, attrs.strip() if bool(attrs.strip()) else None)
            )
            char_count += len(token)

        elif token.startswith("</"):  # end tag
            tag = re.match(r"</(\w+)>", token).group(1)

            if not open_tags or open_tags[-1][0] != tag:
                raise ValueError('Invalid HTML structure')

            del open_tags[-1]  # delete last opened tag
            current_fragment.append(token)
            char_count += len(token)

        else:  # text node
            total_block_size = calculate_total_block_size(char_count, token)
            if total_block_size > char_limit:
                free_space_for_curr_token = char_limit - (char_count + len(close_open_tags()))
                if free_space_for_curr_token < 0:
                    raise ValueError("Can't fragment HTML. Maybe you should reassign the limit?")
                free_space_for_next_tokens = char_limit - (len(reopen_tags()) + len(close_open_tags()))
                text_chunk_for_curr_token, text_chunks = split_text_node(token, free_space_for_curr_token, free_space_for_next_tokens)

                current_fragment.append(text_chunk_for_curr_token)
                current_fragment.append(close_open_tags())
                fragments.append("".join(current_fragment))

                for idx, chunk in enumerate(text_chunks):
                    current_fragment = [reopen_tags()]
                    current_fragment.append(chunk)

                    if idx != len(text_chunks) - 1: # adding current fragments to fragments excluding last one
                        current_fragment.append(close_open_tags())
                        fragments.append("".join(current_fragment))
                else:
                    char_count = len(reopen_tags()) + len(chunk) # actualize char_count

            else:
                current_fragment.append(token)
                char_count += len(token)

    if open_tags:
        raise ValueError('Invalid HTML structure')

    if current_fragment:
        fragments.append("".join(current_fragment))

    return fragments

def main():
    fragments = fragment_html(open(SOURCE_FILE, 'r', encoding='utf-8').read())

    for idx, fragment in enumerate(fragments, 1):
        print(f'fragment #{idx}: {len(fragment)} chars.')
        print(f'{fragment}\n\n')

if __name__ == '__main__':
    main()
