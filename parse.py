from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    OPERATOR = auto()
    VARIABLE = auto()

@dataclass
class Token():
    type: TokenType
    value: str

@dataclass
class Expression():
    token: Token
    arguments: list[Expression]

def tokenize(expression: str) -> list[Token]:
    tokens: list[Token] = []

    operators: set[str] = {
        "+", "-", "/", "(", ")", "="
    }

    buffer: str = ""

    for char in expression:

        if char == " ":
            continue

        if char not in operators:
            buffer += char
            continue

        if buffer:
            token = Token(TokenType.VARIABLE, buffer)
            tokens.append(token)

        token = Token(TokenType.OPERATOR, char)
        tokens.append(token)
        buffer = ""

    if buffer:
        token = Token(TokenType.VARIABLE, buffer)
        tokens.append(token)

    return tokens

def parse_tokens(tokens: list[Token]) -> Expression:
    right = Expression(tokens.pop(), [])
    while tokens:
        
        # if not tokens:
        #     return Expression(right, [])
        
        operator = tokens.pop()
        # left = tokens.pop()
        left = parse_tokens(tokens)
        return Expression(operator, [left, right])

    return right
            
# tokens = tokenize("x'' - x' / (x' + 1) = -3")
# tokens = tokenize("x'' - x' / x' + 1 = -3")
# tokens = tokenize("x'' - x' / x' + 1")

def expression_to_string(expression: Expression) -> str:
    if not expression.arguments:
        return expression.token.value

    arguments: list[str] = []

    for argument in expression.arguments:
        arguments.append(expression_to_string(argument))

    return f"({expression.token.value} {" ".join(arguments)})"

    
tokens = tokenize("x'' / x' - x")
parsed = parse_tokens(tokens)



print(expression_to_string(parsed))

# for token in tokens:
#     parsed.append(f"{token.value} {token.type.name}")

# print(" \n".join(parsed))