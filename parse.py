from dataclasses import dataclass

@dataclass
class Expression():
    token: str
    arguments: list[Expression]

def tokenize(equation: str, operators: set[str]) -> list[str]:
    tokens: list[str] = []
    buffer: str = ""

    for char in equation:

        if char == " ":
            continue

        if char not in operators:
            buffer += char
            continue

        if buffer:
            tokens.append(buffer)

        tokens.append(char)
        buffer = ""

    if buffer:
        tokens.append(buffer)

    return tokens

def expression_to_string(expression: Expression) -> str:
    if not expression.arguments:
        return expression.token

    arguments: list[str] = []

    for argument in expression.arguments:
        arguments.append(expression_to_string(argument))

    return f"({expression.token} {" ".join(arguments)})"

def parse_tokens(tokens: list[str], bindings: dict[str, int], right_binding: float = 0) -> Expression:
    right = Expression(tokens.pop(), [])
    if right.token == ")":
        right = parse_tokens(tokens, bindings, 0)
        tokens.pop()

    while tokens:
        peek = tokens[-1]
        if peek == "(" or bindings[peek] < right_binding:
            break

        operator = tokens.pop()
        left = parse_tokens(tokens, bindings, bindings[operator])
        right = Expression(peek, [left, right])

    return right

def isolate_highest_derivative(expression: Expression):
    if expression.token == "=":
        
        left = expression.arguments[0]
        right = expression.arguments[1]

    token = expression.token

    for argument in expression.arguments:
        isolate_highest_derivative(argument)
        
    
bindings: dict[str, int] = {
    "+": 1,
    "-": 1,
    "/": 2,
    "*": 2,
    "=": 0
}

tokens = tokenize("x'' - 1 = 3", bindings.keys() | {"(", ")"})
parsed = parse_tokens(tokens, bindings)


print(expression_to_string(parsed))

# for token in tokens:
#     parsed.append(f"{token.value} {token.type.name}")

# print(" \n".join(parsed))

# tokens = tokenize("x'' - x' / (x' + 1) = -3")
# tokens = tokenize("x'' - x' / x' + 1 = -3")
# tokens = tokenize("x'' - x' / x' + 1")