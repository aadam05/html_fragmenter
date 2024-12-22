# Fragmentation of HTML into Chunks / Фрагментация HTML на части

## Description / Описание

### English:
This project provides an algorithm for splitting HTML content into fragments, ensuring that each fragment adheres to a character limit while preserving the structure and tags. The algorithm handles edge cases such as unclosed tags, mismatched tags, and missing tags, and raises appropriate exceptions when encountering invalid HTML structures.

### Русский:
Этот проект реализует алгоритм для разделения HTML-контента на фрагменты с учетом ограничений по количеству символов, при этом сохраняя структуру и теги. Алгоритм обрабатывает крайние случаи, такие как незакрытые теги, несовпадение тегов и отсутствие тегов, а также генерирует соответствующие исключения при обнаружении некорректных HTML-структур.

---

## Features / Преимущества

### English:
- The HTML structure is preserved, with all opening and closing tags properly matched.
- Text nodes are correctly split without truncating data.
- Invalid HTML structures trigger exceptions with descriptive error messages.

### Русский:
- Сохранение структуры HTML с правильным открытием и закрытием всех тегов.
- Корректное разделение текстовых узлов без потери данных.
- Исключения с описательными сообщениями об ошибках при наличии некорректных HTML-структур.

---

## Installation / Установка

### English:
To install this project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/aadam05/html_fragmenter.git
    ```
2. Navigate to the project directory:
    ```bash
    cd html_fragmenter
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt # Create venv first
    ```

### Русский:
Для установки проекта выполните следующие шаги:

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/aadam05/html_fragmenter.git
    ```
2. Перейдите в каталог проекта:
    ```bash
    cd html_fragmenter
    ```
3. Установите зависимости:
    ```bash
    pip install -r requirements.txt # Создайте venv сначала
    ```

---

## Usage / Использование

```python
python split_msg.py --max-len=4096 ./html_examples/test4.html # run script / запустить скрипт

python -m unittest discover -s ./tests/ # run tests / запустить тесты
```