import sys


def fragment_html(html, char_limit=240):
    import re
    from typing import List, Tuple
    from html.parser import HTMLParser

    class TagParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tokens = []

        def handle_starttag(self, tag, attrs):
            attr_str = " ".join(f'{key}="{value}"' for key, value in attrs)
            self.tokens.append(f"<{tag} {attr_str}>".strip())

        def handle_endtag(self, tag):
            self.tokens.append(f"</{tag}>")

        def handle_data(self, data):
            if data.strip():
                self.tokens.append(data)

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
        text_chunks = [text[i:i + free_space_for_next_tokens]
                       for i in range(0, len(text), free_space_for_next_tokens)]
        return text_chunk_for_curr_token, text_chunks

    def calculate_total_block_size(char_count: int, token: str):
        """Estimate the size of a current fragment with token, including any closing tags."""
        if token.startswith("<") and not token.startswith("</"):
            # Start tag
            tag = re.match(r"<(\w+)", token).group(1)
            return char_count + len(token) + len(f"</{tag}>") + len(close_open_tags())
        return None

    for idx, token in enumerate(tokens):
        if token.startswith("<") and not token.startswith("</"):  # start tag
            tag, attrs = re.match(r"<(\w+)(.*?)>", token).group(1, 2)
            total_block_size = calculate_total_block_size(char_count, token)
            if total_block_size > char_limit: # BUG: ты не удаляешь теги с open_tags
                current_fragment.append(close_open_tags())
                fragments.append("".join(current_fragment))
                current_fragment = [reopen_tags()]
                char_count = len(reopen_tags())

            current_fragment.append(token)
            open_tags.append(
                (tag, attrs.strip() if bool(attrs.strip()) else None)
            )
            char_count += len(token)

        elif token.startswith("</"):  # end tag
            tag = re.match(r"</(\w+)>", token).group(1)

            for index, item in enumerate(reversed(open_tags)):
                if item[0] == tag:
                    actual_index = len(open_tags) - 1 - index
                    del open_tags[actual_index]
                    break

            current_fragment.append(token)
            char_count += len(token)

        else:  # text node
            total_block_size = char_count + len(token) + len(close_open_tags())
            if total_block_size > char_limit:
                free_space_for_curr_token: int = char_limit - \
                    (char_count + len(close_open_tags()))
                if free_space_for_curr_token < 0:
                    raise ValueError(
                        "free_space_for_curr_token is less than 0. Check your calculations or logic.")
                free_space_for_next_tokens: int = char_limit - \
                    (len(reopen_tags()) + len(close_open_tags()))
                text_chunk_for_curr_token, text_chunks = split_text_node(
                    token, free_space_for_curr_token, free_space_for_next_tokens)

                current_fragment.append(text_chunk_for_curr_token)
                current_fragment.append(close_open_tags())
                fragments.append("".join(current_fragment))

                for chunk in text_chunks:
                    current_fragment = [reopen_tags()]
                    current_fragment.append(chunk)
                    current_fragment.append(close_open_tags())
                    fragments.append("".join(current_fragment))

                current_fragment = [reopen_tags()]
                char_count = len(reopen_tags())
            else:
                current_fragment.append(token)
                char_count += len(token)

    if current_fragment:
        current_fragment.append(close_open_tags())
        fragments.append("".join(current_fragment))

    return fragments


html_example = './example.html'
SOURCE_FILE = sys.argv[2] if sys.argv[2].endswith('.html') else html_example

fragments = fragment_html(open(SOURCE_FILE, 'r', encoding='utf-8').read())
for idx, fragment in enumerate(fragments, 1):
    print(f'fragment #{idx}: {len(fragment)} chars.')
    print(f'{fragment}\n\n')


# import sys
# from bs4 import BeautifulSoup
# from collections.abc import Generator
# from html.parser import *

# html_example = './example.html'

# # MAX_LEN = int(sys.argv[1].split('=')[1]) if sys.argv[1].startswith('--max-len') else 4096
# MAX_LEN = 256
# SOURCE_FILE = sys.argv[2] if sys.argv[2].endswith('.html') else html_example

# def split_message(source: str, max_len=MAX_LEN) -> Generator[str]:
#     """
#     Splits the original message (`source`) into fragments of the specified length (`max_len`).
#     """
#     soup = BeautifulSoup(source, 'html.parser')
#     fragments = []
#     current_fragment = ''
#     stack: list[tuple] = []

#     tag = soup.contents[0]
#     tag_str = str(tag)
#     while True:
#         if not tag_str.strip():
#             continue

#         if len(tag_str) > max_len:
#             stack.append((tag.name, tag.attrs))

#         idx = 0
#         while True:
#             first_child_tag = tag.contents[idx]
#             first_child_tag_str = str(first_child_tag).strip()

#             if first_child_tag_str and len(current_fragment) + len(first_child_tag_str) <= max_len:
#                 current_fragment += first_child_tag_str
#                 first_child_tag_ref = tag.find_all(first_child_tag.name)[0]
#                 first_child_tag_ref.decompose()
#             elif first_child_tag_str and len(current_fragment) + len(first_child_tag_str) > max_len:
#                 if len(first_child_tag_str) > max_len:
#                     pass # FIXME: придумать как зайти в child и разобрать до того как
#                     # tag = first_child_tag
#                     # tag_str = first_child_tag_str
#                     # stack.append((tag.name, tag.attrs))
#                 else:

#                     for i in reversed(stack):
#                         current_fragment = f'<{i[0]} {i[1]}>' + current_fragment + f'<{i[0]}>'
#                     fragments.append(current_fragment)
#                     current_fragment = ''

#             elif idx + 1 < len(tag.contents):
#                 idx += 1
#                 continue

#             break

#     return fragments

# def main():
#     result = split_message(open(SOURCE_FILE, 'r', encoding='utf-8'))

#     # Print the fragments
#     for i, fragment in enumerate(result):
#         print(f"Fragment #{i + 1} ({len(fragment)} chars):\n{fragment}\n")

# if __name__ == '__main__':
#     main()
