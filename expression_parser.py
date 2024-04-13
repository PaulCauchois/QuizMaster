def tokenize_expression(expression):
    tokens = []
    current_token = []

    normalized_expression = expression.replace('&&', 'AND').replace('&', 'AND')
    normalized_expression = normalized_expression.replace('||', 'OR').replace('|', 'OR')
    normalized_expression = normalized_expression.replace('not', 'NOT').replace('Not', 'NOT')
    normalized_expression = normalized_expression.replace('and', 'AND').replace('And', 'AND')
    normalized_expression = normalized_expression.replace('or', 'OR').replace('Or', 'OR')

    operators = {'AND', 'OR', 'NOT', '(', ')'}

    for char in normalized_expression:
        if char.isspace():
            if current_token:
                tokens.append(''.join(current_token))
                current_token = []
        elif char in ['(', ')']:
            if current_token:
                tokens.append(''.join(current_token))
                current_token = []
            tokens.append(char)
        else:
            current_token.append(char)
    if current_token:  # Add the last token if there's any
        tokens.append(''.join(current_token))
    return tokens


def infix_to_postfix(expression):
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
    stack = []  # to keep operators
    postfix = []  # output
    tokens = tokenize_expression(expression)

    for token in tokens:
        if token in precedence:  # If it's an operator, check precedence
            while stack and stack[-1] != '(' and precedence[stack[-1]] >= precedence[token]:
                postfix.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':  # Pop until '(' is encountered
            top_token = stack.pop()
            while top_token != '(':
                postfix.append(top_token)
                top_token = stack.pop()
        else:  # It's a tag
            postfix.append(token.lower())  # Convert tags to lowercase

    while stack:  # Pop any remaining operators
        postfix.append(stack.pop())
    return postfix


def evaluate_postfix(postfix, tags):
    stack = []
    tags = set(tag.lower() for tag in tags)  # Convert to set for efficient lookup

    for token in postfix:
        if token == 'AND':
            right = stack.pop()
            left = stack.pop()
            stack.append(left and right)
        elif token == 'OR':
            right = stack.pop()
            left = stack.pop()
            stack.append(left or right)
        elif token == 'NOT':
            operand = stack.pop()
            stack.append(not operand)
        else:
            stack.append(token in tags)

    return stack.pop()


def parse_expression(expression, tags):
    """
    Parses the logical expression on the tags and returns the result.
    :param expression: A logical expression, with parentheses, AND, OR, and NOT.
    :param tags: The list of tags to evaluate the expression on.
    :return: True if the list of tags follows the expression, False otherwise.
    """
    postfix = infix_to_postfix(expression)
    return evaluate_postfix(postfix, tags)
