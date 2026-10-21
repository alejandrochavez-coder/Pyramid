from dataclasses import dataclass
from typing import Callable

@dataclass
class Expression():
    token: str
    arguments: list[Expression]

@dataclass
class Binding():
    priority: int
    single_right: Callable[[], str]

def tokenize(equation: str, bindings: dict[str, Binding]) -> list[str]:
    tokens: list[str] = []
    buffer: str = ""

    for char in equation:

        if char == " ":
            continue

        if char not in bindings.keys() | {"(", ")"}:
            buffer += char
            continue

        if buffer:
            tokens.append(buffer) 
        else:
            tokens.append(bindings[char].single_right())

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

def parse_tokens(tokens: list[str], bindings: dict[str, Binding], right_binding: float = 0) -> Expression:
    right = Expression(tokens.pop(), [])
    if right.token == ")":
        right = parse_tokens(tokens, bindings, 0)
        tokens.pop()

    while tokens:
        peek = tokens[-1]
        if peek == "(" or bindings[peek].priority < right_binding:
            break

        operator = tokens.pop()
        left = parse_tokens(tokens, bindings, bindings[operator].priority)
        right = Expression(peek, [left, right])

    return right

def isolate_highest_derivative(expression: Expression):
    for argument in expression.arguments:
        isolate_highest_derivative(argument)

    print(expression.token)
    # if expression.token == "=":
        
    #     left = expression.arguments[0]
    #     right = expression.arguments[1]

    # token = expression.token

    # for argument in expression.arguments:
    #     isolate_highest_derivative(argument)

def _raise(exception: Exception):
    raise exception
    
bindings: dict[str, Binding] = {
    "+": Binding(1, lambda: "0"),
    "-": Binding(1, lambda: "0"),
    "/": Binding(2, lambda: _raise(ValueError("Can't do / without two sides"))),
    "*": Binding(2, lambda: _raise(ValueError("Can't do * without two sides"))),
    "=": Binding(0, lambda: _raise(ValueError("Invalid use of =")))
}

tokens = tokenize("x'' - 1 = - 3 - 5", bindings)
print(tokens)
parsed = parse_tokens(tokens, bindings)
isolate_highest_derivative(parsed)
# print(expression_to_string(parsed))

# for token in tokens:
#     parsed.append(f"{token.value} {token.type.name}")

# print(" \n".join(parsed))

# tokens = tokenize("x'' - x' / (x' + 1) = -3")
# tokens = tokenize("x'' - x' / x' + 1 = -3")
# tokens = tokenize("x'' - x' / x' + 1")