from dataclasses import dataclass
from typing import Callable
import string

@dataclass
class Expression():
    token: str
    arguments: list[Expression]

@dataclass
class Binding():
    priority: int
    default: str
    evaluation: Callable[[float, float], float] | None = None

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

        tokens.append(char)
        buffer = ""

    if buffer:
        tokens.append(buffer)

    return tokens

# https://en.wikipedia.org/wiki/Polish_notation
def expression_to_string(expression: Expression) -> str:
    if not expression.arguments:
        return expression.token

    arguments: list[str] = []

    for argument in expression.arguments:
        arguments.append(expression_to_string(argument))

    return f"({expression.token} {" ".join(arguments)})"

# https://en.wikipedia.org/wiki/Operator-precedence_parser
def tokens_to_expression(tokens: list[str], bindings: dict[str, Binding], right_binding: float = 0) -> Expression:
    binding = bindings.get(tokens[-1])
    if binding:
        tokens.append(binding.default)
    
    right = Expression(tokens.pop(), [])
    if right.token == ")":
        right = tokens_to_expression(tokens, bindings, 0)
        tokens.pop()
        
    while tokens:
        peek = tokens[-1]
        if peek == "(" or bindings[peek].priority < right_binding:
            break

        operator = tokens.pop()

        if tokens:
            left = tokens_to_expression(tokens, bindings, bindings[operator].priority)
        else:
            left = Expression(bindings[operator].default, None)

        right = Expression(peek, [left, right])

    return right

# # https://en.wikipedia.org/wiki/Depth-first_search
# def isolate_highest_derivative(expression: Expression):
#     stack: list[Expression] = []
#     stack.append(expression)

#     while stack:
#         current = stack.pop()
#         token = current.token

#         # print(token)
#         if current.arguments:
#             pass

#         stack.extend(current.arguments)

    # print(expression.token)

    # for argument in expression.arguments:
    #     isolate_highest_derivative(argument)

    # if expression.token == "=":
        
    #     left = expression.arguments[0]
    #     right = expression.arguments[1]

# https://en.wikipedia.org/wiki/Tree_traversal#Reverse_post-order,_RLN
def pre_compute_expression_leaves(expression: Expression, bindings: dict[str, Binding]) -> Expression:
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

# def pre_compute_expression_communitatives(expression: Expression) -> Expression:
#     if not expression.arguments:
#         return expression

#     expression.arguments[0] = pre_compute_expression_communitatives(expression.arguments[0])
#     expression.arguments[1] = pre_compute_expression_communitatives(expression.arguments[1])

#     if expression.token == "-":
#         right = expression.arguments[1]
#         # right.token = f"-{right.token}"

#         # return Expression("+", [expression.arguments[0], right])
#         print(expression_to_string(expression))
#     #     right = expression.arguments[1]

#     #     expression.arguments[1] = Expression(f"-{right.token}", None)
#     #     expression.token = "+"

#     return expression

def simplify_expression(expression: Expression) -> Expression:

    if not expression.arguments:
        return expression

    for index, argument in enumerate(expression.arguments):
        expression.arguments[index] = simplify_expression(argument)

    token = expression.token

    simplified = Expression("+", [])
    for argument in expression.arguments:
        if token != "+":
            continue
        
        if argument.token == "+":
            simplified.arguments.extend(argument.arguments)
        else:
            simplified.arguments.append(argument)

    print(expression_to_string(simplified))
    if simplified.arguments:
        return simplified
    
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
    
bindings: dict[str, Binding] = {
    "+": Binding(1, "0", lambda a, b: a + b),
    "-": Binding(1, "0", lambda a, b: a - b),
    "/": Binding(2, "1", lambda a, b: a / b),
    "*": Binding(2, "1", lambda a, b: a * b),
    "=": Binding(0, "x'")
}

# tokens = tokenize("- 1 + (x'' * 3) - 1 + 1 + x * x'", bindings)
# tokens = tokenize("x + 2 * 3 + 7 + 2 - 5 * 3", bindings)
# tokens = tokenize("- 1 + (x'' * 3) - 1 + 1 + x * x'", bindings)
tokens = tokenize("4 *", bindings)
print(tokens)

expression = tokens_to_expression(tokens, bindings)
print(expression_to_string(expression))
# if tokens.count("=") != 1:
#     raise ValueError("Need valid equation")

# expression = simplify_expression(expression)
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