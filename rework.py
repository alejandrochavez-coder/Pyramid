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
class Invertible:
    pass

class UnaryPostfix:
    pass

class Operand:
    pass

class OpenParenthesis:
    pass

class CloseParenthesis:
    pass

class LeftAssociative:
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

def simplify_operators(expression: Exception, operators: dict[str, dict[type, object]]) -> Expression:
    minus_one_token = Token({Value: Value("-1"), Operand: Operand()})
    minus_one = Expression(minus_one_token, [])
    value = cast(Value, expression.token.components[Value]).value

    if value == "/":
        simplified = Expression(Token(operators["*"]), [])
        for argument in expression.arguments:
            simplified_argument = Expression(Token(operators["^"]), [argument, minus_one])
            simplified.arguments.append(simplified_argument)

        simplified.arguments[0] = expression.arguments[0]
        return simplified

    if value == "-":
        simplified = Expression(Token(operators["+"]), [])
        for argument in expression.arguments:
            simplified_argument = Expression(Token(operators["*"]), [argument, minus_one])
            simplified.arguments.append(simplified_argument)

        simplified.arguments[0] = expression.arguments[0]
        return simplified

    return expression

def simplify_associatives(expression: Expression) -> Expression:
    if not LeftAssociative in expression.token.components:
        return expression

    value = cast(Value, expression.token.components[Value]).value
    simplified = Expression(expression.token, [])

    for argument in expression.arguments:
        argument_value = cast(Value, expression.token.components[Value]).value

        if value == argument_value:
            simplified.arguments.extend(argument.arguments)
        else:
            simplified.arguments.append(argument)

    return simplified
        


def simplify(expression: Expression, operators: dict[str, dict[type, object]]) -> Expression:

    if not expression.arguments:
        return expression
    
    for index, argument in enumerate(expression.arguments):
        expression.arguments[index] = simplify(argument, operators)

    # value = cast(Value, expression.token.components[Value]).value
    # minus_one_token = Token({Value: Value("-1"), Operand: Operand()})
    # minus_one = Expression(minus_one_token, [])

    expression = simplify_operators(expression, operators)
    # expression = simplify_associatives(expression)
    
    # simplified = Expression(expression.token, [])

    # for argument in expression.arguments:
    #     argument_value = cast(Value, expression.token.components[Value]).value
    #     if not LeftAssociative in expression.token.components:
    #         simplified.arguments.append(argument)
    #         continue

    #     if value != argument_value:
    #         simplified.arguments.append(argument)
    #         continue

    #     if LeftAssociative in argument.token.components:
    #         simplified.arguments.extend(argument.arguments)

        
        
    return expression

operators: dict[str, dict[type, object]] = {
    "+": {Value: Value("+"), Operator: Operator(priority=1), UnaryPostfix: UnaryPostfix(), LeftAssociative: LeftAssociative()},
    "-": {Value: Value("-"), Operator: Operator(priority=1), UnaryPostfix: UnaryPostfix()},
    "*": {Value: Value("*"), Operator: Operator(priority=2), LeftAssociative: LeftAssociative()},
    "/": {Value: Value("/"), Operator: Operator(priority=2)},
    "^": {Value: Value("^"), Operator: Operator(priority=3), LeftAssociative: LeftAssociative()},
    "(": {OpenParenthesis: OpenParenthesis()},
    ")": {CloseParenthesis: CloseParenthesis()}
}

tokens = tokenize("a / b * b ^ 2 - 2", operators)

try:
    expression = parse(tokens)
    expression = simplify(expression, operators)
    print(expression)
except ValueError as error:
    print(str(error))