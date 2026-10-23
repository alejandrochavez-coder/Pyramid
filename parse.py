from dataclasses import dataclass
from typing import Callable
from enum import Enum, auto
import itertools

class OperatorProperties(Enum):
    RIGHT_ASSOCIATIVE = auto()
    UNARY_POSTFIX = auto()
    BINARY = auto()

@dataclass
class Expression():
    token: str
    arguments: list[Expression]

@dataclass
class OperatorInfo():
    priority: int
    properties: list[OperatorProperties]
    # identity: str

# https://en.wikipedia.org/wiki/Polish_notation
def expression_to_string(expression: Expression) -> str:
    if not expression.arguments:
        return expression.token

    arguments: list[str] = []

    for argument in expression.arguments:
        arguments.append(expression_to_string(argument))

    return f"({expression.token} {" ".join(arguments)})"

# https://en.wikipedia.org/wiki/Tree_traversal#Reverse_post-order,_RLN
def pre_compute_expression_leaves(expression: Expression, bindings: dict[str, OperatorInfo]) -> Expression:
    if not expression.arguments:
        return expression
    
    expression.arguments[0] = pre_compute_expression_leaves(expression.arguments[0], bindings)
    expression.arguments[1] = pre_compute_expression_leaves(expression.arguments[1], bindings)

    binding = bindings.get(expression.token)
    if not binding or not binding.evaluation:
        return expression

    left = expression.arguments[0].token
    right = expression.arguments[1].token

    try:
        result = binding.evaluation(float(left), float(right))
        return Expression(str(result), None)
    
    except ValueError:
        return expression

def simplify_asociatives(expression: Expression, bindings: dict[str, OperatorInfo]) -> Expression:
    token = expression.token
    binding = bindings.get(token)

    if not binding or OperatorProperties.RIGHT_ASSOCIATIVE not in binding.properties:
        return expression

    simplified = Expression(token, [])

    for argument in expression.arguments:

        if argument.token == token:
            simplified.arguments.extend(argument.arguments)
        else:
            simplified.arguments.append(argument)

    return simplified

def simplify_identity(expression: Expression, bindings: dict[str, OperatorInfo]) -> Expression:
    token = expression.token
    binding = bindings.get(token)

    if not binding or OperatorProperties.RIGHT_ASSOCIATIVE not in binding.properties:
        return expression

    simplified = Expression(token, [])

    for left, right in list(itertools.combinations(expression.arguments, 2)):
        if left.token == binding.identity:
            simplified.arguments.append(right)
            continue
    
        if right.token == binding.identity:
            simplified.arguments.append(left)
            continue

        # print(expression_to_string(left))
        # print(expression_to_string(right))
        # print()

        # A^-1 * A = 1
        if (left.token == "^" and left.arguments[1].token == "-1" and left.arguments[0].token == right.token or
            right.token == "^" and right.arguments[1].token == "-1" and right.arguments[0].token == left.token):

            simplified.arguments.append(Expression("1", None))
            continue

        if not simplified.arguments:
            simplified.arguments.append(left)

        simplified.arguments.append(right)

    return simplified

# def simplify_

# https://en.wikipedia.org/wiki/Tree_traversal#Post-order,_LRN
def simplify_expression(expression: Expression, bindings: dict[str, OperatorInfo]) -> Expression:

    if not expression.arguments:
        return expression

    for index, argument in enumerate(expression.arguments):
        expression.arguments[index] = simplify_expression(argument, bindings)

    token = expression.token

    expression = simplify_asociatives(expression, bindings)
    expression = simplify_identity(expression, bindings)

    if len(expression.arguments) == 1 and not expression.arguments[0].arguments:
        simplified = Expression(expression.arguments[0].token, None)
        expression = simplify_expression(simplified, bindings)

    if token == "-":
        right = expression.arguments[1]
        right = Expression("*", [Expression("-1", None), right])

        simplified = Expression("+", [expression.arguments[0], right])
        expression = simplify_expression(simplified, bindings)

    if token == "/":
        right = expression.arguments[1]
        right = Expression("^", [right, Expression("-1", None)])

        simplified = Expression("*", [expression.arguments[0], right])
        expression = simplify_expression(simplified, bindings)
    
    return expression

def find_highest_derivative(expression: Expression) -> str:
    derivative_degree = expression.token.count("'")
    derivative = ""
    
    if not expression.arguments:
        return expression.token

    for argument in expression.arguments:
        derivative_attempt = find_highest_derivative(argument)
        attempt_degree = derivative_attempt.count("'")

        if attempt_degree > derivative_degree:
            derivative_degree = attempt_degree
            derivative = derivative_attempt

    return derivative

def tokenize(equation: str, bindings: dict[str, OperatorInfo]) -> list[str]:
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

        tokens.append(char)
        buffer = ""

    if buffer:
        tokens.append(buffer)

    return tokens

# https://en.wikipedia.org/wiki/Operator-precedence_parser
def tokens_to_expression(tokens: list[str], bindings: dict[str, OperatorInfo], right_binding: float = 0) -> Expression:
    right = Expression(tokens.pop(), [])

    if right.token == ")":
        right = tokens_to_expression(tokens, bindings, 0)
        tokens.pop()
        
    while tokens:
        peek = tokens[-1]

        if peek == "(" or bindings[peek].priority < right_binding:
            break

        operator = tokens.pop()

        if OperatorProperties.UNARY_POSTFIX in bindings[peek].properties and (not tokens or tokens[-1] in bindings):
            right = Expression(operator, [right])
            continue

        if OperatorProperties.BINARY in bindings[peek].properties and tokens:
            left = tokens_to_expression(tokens, bindings, bindings[operator].priority)
            right = Expression(operator, [left, right])

    return right
    
bindings: dict[str, OperatorInfo] = {
    "+": OperatorInfo(1, [OperatorProperties.RIGHT_ASSOCIATIVE, OperatorProperties.BINARY, OperatorProperties.UNARY_POSTFIX]),
    "-": OperatorInfo(1, [OperatorProperties.BINARY, OperatorProperties.UNARY_POSTFIX]),
    # "*": Operator(2, "1", [OperatorProperties.RIGHT_ASSOCIATIVE]),
    # "/": Operator(2, "1", []),
    # "^": Operator(3, "1", []),
    # "=": Operator(0, "x'", [])
}

# tokens = tokenize("- 1 + (x'' * 3) - 1 + 1 + x * x'", bindings)
# tokens = tokenize("x + 2 * 3 + 7 + 2 - 5 * 3", bindings)
# tokens = tokenize("- 1 + (x'' * 3) - 1 + 1 + x * x'", bindings)
tokens = tokenize("--1 - (1 + 3)", bindings)
# print(tokens)
expression = tokens_to_expression(tokens, bindings)
# expression = simplify_expression(expression, bindings)


print(expression_to_string(expression))


# if tokens.count("=") != 1:
#     raise ValueError("Need valid equation")

# print(expression_to_string(expression))

# left_highest = find_highest_derivative(expression.arguments[0])
# right_highest = find_highest_derivative(expression.arguments[1])

# derivative = find_highest_derivative(expression)
# print(derivative)


# expression = pre_compute_expression_leaves(expression, bindings)
# expression = pre_compute_expression_communitatives(expression)


# for token in tokens:
#     parsed.append(f"{token.value} {token.type.name}")

# print(" \n".join(parsed))

# tokens = tokenize("x'' - x' / (x' + 1) = -3")
# tokens = tokenize("x'' - x' / x' + 1 = -3")
# tokens = tokenize("x'' - x' / x' + 1")