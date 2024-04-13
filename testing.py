import unittest
from file_parser import parse_quiz_and_flashcards


class TestParseQuizAndFlashcards(unittest.TestCase):

    def test_successful_parsing(self):
        content = """
Q: What is the capital of France?
O:
A. Paris
B. London
C. Berlin
D. Madrid
A: A
T: geography, capitals
END
F: Largest planet in our Solar System
A: Jupiter
T: astronomy
END
"""
        expected = [
            {'type': 'quiz', 'question': 'What is the capital of France?',
             'options': {'A': 'Paris', 'B': 'London', 'C': 'Berlin', 'D': 'Madrid'}, 'answer': 'A',
             'tags': ['geography', 'capitals']},
            {'type': 'flashcard', 'fact': 'Largest planet in our Solar System', 'answer': 'Jupiter',
             'tags': ['astronomy']}
        ]
        items, error_code = parse_quiz_and_flashcards(content)
        self.assertEqual(error_code, 0)
        self.assertEqual(items, expected)

    def test_error_code_1_unexpected_error(self):
        # This would typically test for unexpected errors, like file read errors.
        # Here, you'd simulate or mock a scenario where an unexpected error occurs.
        pass  # Implement as needed

    def test_error_code_2_item_not_ended(self):
        content = """
Q: What is the capital of France?
O:
A. Paris
B. London
Q: What is the tallest mountain?
O:
A. Everest
END
"""
        _, error_code = parse_quiz_and_flashcards(content)
        self.assertEqual(error_code, 2)

    def test_error_code_3_flashcard_contains_options(self):
        content = """
F: Formula for the area of a circle
O:
A. pi*r^2
END
"""
        _, error_code = parse_quiz_and_flashcards(content)
        self.assertEqual(error_code, 3)

    def test_error_code_4_unknown_line_argument(self):
        content = """
Q: What is the capital of France?
X: Unexpected line
A: A
END
"""
        _, error_code = parse_quiz_and_flashcards(content)
        self.assertEqual(error_code, 4)

    def test_error_code_5_missing_arguments(self):
        # For flashcards missing answers
        content_flashcard_missing_answer = """
F: Largest planet in our Solar System
END
"""
        _, error_code = parse_quiz_and_flashcards(content_flashcard_missing_answer)
        self.assertEqual(error_code, 5)

    def test_error_code_6_answer_not_in_options(self):
        content = """
Q: What is the capital of France?
O:
A. Berlin
B. London
C. Berlin
D. Madrid
A: Z
END
"""
        _, error_code = parse_quiz_and_flashcards(content)
        self.assertEqual(error_code, 6)

    def test_error_code_7_argument_outside_item_block(self):
        content = """
A: Paris
END
"""
        _, error_code = parse_quiz_and_flashcards(content)
        self.assertEqual(error_code, 7)

if __name__ == '__main__':
    unittest.main()
