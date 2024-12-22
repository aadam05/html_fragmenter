import re
import sys
from typing import List, Tuple
from html.parser import HTMLParser
from collections.abc import Generator

# Default configuration values
html_example = './html_examples/test3.html'

# Check command-line arguments for max length and source file
if len(sys.argv) > 1 and sys.argv[1].startswith('--max-len'):
    MAX_LEN = int(sys.argv[1].split('=')[1])
else:
    MAX_LEN = 1024 # 4096

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

class HTMLFragmenter:
    def __init__(self, html, char_limit=MAX_LEN):
        self.html = html
        self.char_limit = char_limit

        self.parser = TagParser()
        self.parser.feed(html)
        self.tokens = self.parser.tokens

        self.fragments = []
        self.current_fragment = []
        self.char_count = 0
        self.open_tags: List[Tuple[str, str]] = []

    def __close_open_tags(self):
        return "".join(f"</{tag}>" for tag, attr in reversed(self.open_tags))

    def __reopen_tags(self):
        return "".join(f"<{tag} {attr}>" if attr else f"<{tag}>" for tag, attr in self.open_tags)

    def __split_text_node(self, text: str, free_space_for_curr_token: int, free_space_for_next_tokens: int):
        """Split long text nodes into smaller chunks."""
        text_chunk_for_curr_token = text[0:free_space_for_curr_token]
        text = text[free_space_for_curr_token:]
        text_chunks = [text[i:i + free_space_for_next_tokens] for i in range(0, len(text), free_space_for_next_tokens)]
        return text_chunk_for_curr_token, text_chunks

    def __calculate_total_block_size(self, token: str):
        """Estimate the size of a current fragment with token, including any closing tags."""
        
        is_open_tag = token.startswith("<")
        is_close_tag = token.startswith("</")
        
        if is_open_tag and not is_close_tag:
            tag = re.match(r"<(\w+)", token).group(1)
            return self.char_count + len(token) + len(f"</{tag}>") + len(self.__close_open_tags())
        elif is_close_tag:
            return None
        else:  # otherwise, it's a text node.
            return self.char_count + len(token) + len(self.__close_open_tags())
    
    def fragment_html(self):
        for token in self.tokens:
            if token.startswith("<") and not token.startswith("</"):  # start tag
                tag, attrs = re.match(r"<(\w+)(.*?)>", token).group(1, 2)
                total_block_size = self.__calculate_total_block_size(token)
                if total_block_size > self.char_limit:
                    self.current_fragment.append(self.__close_open_tags())
                    self.fragments.append("".join(self.current_fragment))

                    if len(self.__reopen_tags()) + len(token) + len(self.__close_open_tags()) > self.char_limit:
                        raise ValueError("Either you set a small limit, or the HTML is too deep.")

                    self.current_fragment = [self.__reopen_tags()]
                    self.char_count = len(self.__reopen_tags())

                self.current_fragment.append(token)
                self.open_tags.append(
                    (tag, attrs.strip() if bool(attrs.strip()) else None)
                )
                self.char_count += len(token)

            elif token.startswith("</"):  # end tag
                tag = re.match(r"</(\w+)>", token).group(1)

                if not self.open_tags or self.open_tags[-1][0] != tag:
                    raise ValueError('Invalid HTML structure')

                del self.open_tags[-1]  # delete last opened tag
                self.current_fragment.append(token)
                self.char_count += len(token)

            else:  # text node
                total_block_size = self.__calculate_total_block_size(token)
                if total_block_size > self.char_limit:
                    free_space_for_curr_token = self.char_limit - (self.char_count + len(self.__close_open_tags()))
                    if free_space_for_curr_token < 0:
                        raise ValueError("Can't fragment HTML. Maybe you should reassign the limit?")
                    free_space_for_next_tokens = self.char_limit - (len(self.__reopen_tags()) + len(self.__close_open_tags()))
                    text_chunk_for_curr_token, text_chunks = self.__split_text_node(token, free_space_for_curr_token, free_space_for_next_tokens)

                    self.current_fragment.append(text_chunk_for_curr_token)
                    self.current_fragment.append(self.__close_open_tags())
                    self.fragments.append("".join(self.current_fragment))

                    for idx, chunk in enumerate(text_chunks):
                        self.current_fragment = [self.__reopen_tags()]
                        self.current_fragment.append(chunk)

                        if idx != len(text_chunks) - 1: # adding current fragments to fragments excluding last one
                            self.current_fragment.append(self.__close_open_tags())
                            self.fragments.append("".join(self.current_fragment))
                    else:
                        self.char_count = len(self.__reopen_tags()) + len(chunk) # actualize char_count

                else:
                    self.current_fragment.append(token)
                    self.char_count += len(token)

        if self.open_tags:
            raise ValueError('Invalid HTML structure')

        if self.current_fragment:
            self.fragments.append("".join(self.current_fragment))

        return self.fragments

def fragment_html(html, char_limit=MAX_LEN):
    """
    DEPRECATED. Use HTMLFragmenter class instead.
    """
    return HTMLFragmenter(html, char_limit).fragment_html()

def main():
    # FIXME: maybe should i use conext manager?
    # with open(SOURCE_FILE, 'r', encoding='utf-8').read() as html_str:
        # fragments = fragment_html(html_str)
    
    html_str = open(SOURCE_FILE, 'r', encoding='utf-8').read()
    fragments = HTMLFragmenter(html_str).fragment_html()

    for idx, fragment in enumerate(fragments, 1):
        print(f'fragment #{idx}: {len(fragment)} chars.')
        print(f'{fragment}\n\n')

if __name__ == '__main__':
    main()
