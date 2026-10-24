from dataclasses import dataclass
from typing import Callable, cast
from enum import Enum, auto
import itertools

@dataclass
class Token:
    components: dict[type, object]

@dataclass
class Value:
    value: str

@dataclass
class Operator:
    priority: int

@dataclass
class LeftIdentity:
    identity: str

@dataclass
class RightIdentity:
    identity: str

@dataclass
class OperatorInverse:
    pass

class UnaryPostfix:
    pass

class Operand:
    pass

class OpenParenthesis:
    pass

class CloseParenthesis:
    pass

class Associative:
    pass

@dataclass
class Expression():
    token: Token
    arguments: list[Expression]

    def __str__(self):

        value_component = cast(Value, self.token.components.get(Value))
        if not value_component:
            return ""
        
        if Operand in self.token.components:
            return value_component.value

        buffer: list[str] = []

        for argument in self.arguments:
            buffer.append(str(argument))

        return f"({value_component.value} {" ".join(buffer)})"

def tokenize(equation: str, operators: dict[str, dict[type, object]]) -> list[Token]:
    tokens: list[Token] = []
    buffer: str = ""

    for char in equation:

        if char == " ":
            continue

        if char not in operators:
            buffer += char
            continue

        if buffer:
            token = Token({Value: Value(buffer), Operand: Operand()})
            tokens.append(token) 

        tokens.append(Token(operators[char]))
        buffer = ""

    if buffer:
        token = Token({Value: Value(buffer), Operand: Operand()})
        tokens.append(token) 

    return tokens

def parse(tokens: list[Token], right_priority: int = 0) -> Expression:
    if not tokens or OpenParenthesis in tokens[-1].components:
        raise ValueError("Invalid Equation")
    
    right = Expression(tokens.pop(), [])
    if CloseParenthesis in right.token.components:
        right = parse(tokens)
        tokens.pop()

    while tokens:
        operator = tokens[-1]
        operator_component = cast(Operator, operator.components.get(Operator))

        if OpenParenthesis in operator.components:
            break

        if operator_component.priority < right_priority:
            break

        tokens.pop()

        if tokens and (CloseParenthesis in tokens[-1].components or Operand in tokens[-1].components):
            left = parse(tokens, operator_component.priority)
            right = Expression(operator, [left, right])
        elif UnaryPostfix in operator.components:
            right = Expression(operator, [right])
        else:
            raise ValueError("Invalid Equation")

    return right

# def remove_non_essential_operators(expression: Expression, operators: dict[str, dict[type, object]]) -> Expression:
#     minus_one_token = Token({Value: Value("-1"), Operand: Operand()})
#     minus_one = Expression(minus_one_token, [])
#     value = cast(Value, expression.token.components[Value]).value

#     if value == "/":
#         simplified = Expression(Token(operators["*"]), [])
#         for argument in expression.arguments:
#             simplified_argument = Expression(Token(operators["^"]), [argument, minus_one])
#             simplified.arguments.append(simplified_argument)

#         simplified.arguments[0] = expression.arguments[0]
#         return simplified

#     if value == "-":
#         simplified = Expression(Token(operators["+"]), [])
#         for argument in expression.arguments:
#             simplified_argument = Expression(Token(operators["*"]), [argument, minus_one])
#             simplified.arguments.append(simplified_argument)

#         simplified.arguments[0] = expression.arguments[0]
#         return simplified

#     return expression

def group_associatives(expression: Expression) -> Expression:
    if not Associative in expression.token.components:
        return expression

    operator_value = cast(Value, expression.token.components[Value]).value
    simplified = Expression(expression.token, [])

    for argument in expression.arguments:
        argument_value = cast(Value, argument.token.components[Value]).value

        if operator_value == argument_value:
            simplified.arguments.extend(argument.arguments)
        else:
            simplified.arguments.append(argument)

    return simplified

def simplify_identities(expression: Expression) -> Expression:
    if (Operand in expression.token.components or
        (not RightIdentity in expression.token.components and
        not LeftIdentity in expression.token.components)):

        return expression

    simplified_expressions: list[Expression] = []

    right_identity_component = cast(RightIdentity, expression.token.components.get(RightIdentity))
    left_identity_component = cast(LeftIdentity, expression.token.components.get(LeftIdentity))

    for left, right in list(itertools.pairwise(expression.arguments)):
        right_value = cast(Value, right.token.components[Value]).value
        left_value = cast(Value, left.token.components[Value]).value

        is_right_identity = right_identity_component and right_value == right_identity_component.identity
        is_left_identity = left_identity_component and left_value == left_identity_component.identity

        if is_right_identity and is_left_identity:
            continue

        if is_left_identity:
            simplified_expressions.append(right)
            continue

        if is_right_identity:
            simplified_expressions.append(left)
            continue

        # if not simplified_expressions:
        #     simplified_expressions.append(left)

        simplified_expressions.append(right)

    if not simplified_expressions:
        zero_token = Token({Value: Value("0"), Operand: Operand()})
        return Expression(zero_token, [])

    return Expression(expression.token, simplified_expressions)

def simplify(expression: Expression) -> Expression:

    if not expression.arguments:
        return expression
    
    for index, argument in enumerate(expression.arguments):
        expression.arguments[index] = simplify(argument)

    # expression = remove_non_essential_operators(expression, operators)
    expression = group_associatives(expression)
    print(expression)
    expression = simplify_identities(expression)
    print(expression)
    print()
        
    return expression

operators: dict[str, dict[type, object]] = {
    "(": {OpenParenthesis: OpenParenthesis()},
    ")": {CloseParenthesis: CloseParenthesis()}
}

operators["+"] = {
    Value: Value("+"),
    Operator: Operator(priority=1),
    UnaryPostfix: UnaryPostfix(),
    Associative: Associative(),
    RightIdentity: RightIdentity("0"),
    LeftIdentity: LeftIdentity("0")
}

operators["-"] = {
    Value: Value("-"),
    Operator: Operator(priority=1),
    UnaryPostfix: UnaryPostfix(),
    RightIdentity: RightIdentity("0")
}

operators["*"] = {
    Value: Value("*"),
    Operator: Operator(priority=2), 
    Associative: Associative(),
    RightIdentity: RightIdentity("1"),
    LeftIdentity: LeftIdentity("1")
}

operators["/"] = {
    Value: Value("/"), 
    Operator: Operator(priority=2),
    RightIdentity: RightIdentity("1")
}

operators["^"] = {
    Value: Value("^"), 
    Operator: Operator(priority=3), 
    Associative: Associative()
}

tokens = tokenize("2 + a + 0 + 0 - 0", operators)

try:
    expression = parse(tokens)
    expression = simplify(expression)
    print(expression)
except ValueError as error:
    print(str(error))