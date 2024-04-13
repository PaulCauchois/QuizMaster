from typing import List, Dict, Tuple
import uuid


def parse_quiz_and_flashcards(content: str) -> Tuple[List[Dict], int]:
    """
    Parses content with quizzes and flashcards into a list of dictionaries.

    :param content: The content containing quiz and flashcard items.

    :returns: Tuple[List[Dict], int]: A list of quiz and flashcard items
      as dictionaries, and an error code indicating the parsing status :
      - 1: Unexpected error
      - 2: Item started before the previous one ended
      - 3: Flashcard block contains options
      - 4: Unknown line argument
      - 5: Missing arguments
      - 6: Answer not in options
      - 7: Argument outside of item block
      - 8: Empty content
    """
    items = {}
    item = {}
    options = []
    in_options = False

    if not content:
        return items, 8

    try:
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                if in_options and line[1] == ':':
                    in_options = False
                command, _, content = line.partition(':') if not in_options else line.partition('.')
                content = content.strip()

                if not item and command not in ('Q', 'F'):
                    return items, 7

                match command:
                    case 'Q':
                        if item:  # Start of a new item before the previous one ended
                            return items, 2
                        item = {'type': 'quiz', 'question': content}
                    case 'F':
                        if item:  # Start of a new item before the previous one ended
                            return items, 2
                        item = {'type': 'flashcard', 'fact': content}
                    case 'O':
                        if item.get('type') == 'flashcard':
                            return items, 3
                        options = dict()
                        in_options = True
                    case _ if in_options:
                        options[command] = content
                    case 'A':
                        if item.get('type') == 'quiz':
                            item['options'] = options
                            in_options = False
                            if content not in options:
                                return items, 6  # Answer not in options
                        item['answer'] = content
                    case 'E':
                        item['explanation'] = content
                    case 'T':
                        item['tags'] = [tag.strip() for tag in content.split(',')]
                    case 'END':
                        if item['type'] == 'quiz' and ('options' not in item or 'answer' not in item):
                            return items, 5
                        if item['type'] == 'flashcard' and 'answer' not in item:
                            return items, 5
                        items[str(uuid.uuid1())] = item
                        item = {}  # Reset for the next item
                        options = []
                    case _:
                        return items, 4  # Unknown line argument

    except Exception as e:
        print(f"An error occurred: {e}")
        return items, 1

    if item:
        return items, 2

    return items, 0


def parse_quiz_and_flashcards_file(file_path: str) -> Tuple[Dict[str, Dict], int]:
    """
    Wrapper to parse files directly.
    """
    with open(file_path, "r") as file:
        return parse_quiz_and_flashcards(file.read())


# Example usage:
if __name__ == '__main__':
    content = """
Q: What is the capital of France?
O:
A. Paris
B. London
A: A
E: Paris is the capital of France.
T: geography, capitals
END
F: Bonjour
A: Hello
T: language, english, french
END
"""
    items, error_code = parse_quiz_and_flashcards(content)
    print(error_code)
    print(items)