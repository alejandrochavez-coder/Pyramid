from dataclasses import dataclass
from typing import Callable, cast

@dataclass
class Token:
    components: dict[type, object]

@dataclass
class Value:
    value: str

@dataclass
class Operator:
    priority: int

# https://en.wikipedia.org/wiki/Identity_element
@dataclass
class Identity:
    identity: str

# https://en.wikipedia.org/wiki/Inverse_function
@dataclass
class InverseComponents:
    components: dict[type, object]

# https://en.wikipedia.org/wiki/Inverse_element
@dataclass
class ElementInverse:
    operator_components: dict[type, object]
    right_operand: Expression

# https://en.wikipedia.org/wiki/Absorbing_element
@dataclass
class AbsorbingElement:
    element: str

class BasicOperator:
    pass

# https://en.wikipedia.org/wiki/Unary_operation
class UnaryPrefix:
    pass

class Operand:
    pass

class OpenParenthesis:
    pass

class CloseParenthesis:
    pass

# https://en.wikipedia.org/wiki/Operator_associativity
class Associative:
    pass

class UnaryIdentity:
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
        elif UnaryPrefix in operator.components:
            right = Expression(operator, [right])
        else:
            raise ValueError("Invalid Equation")

    return right

def simplify_absorving_element(expression: Expression) -> Expression:
    if AbsorbingElement not in expression.token.components:
        return expression

    absorving_element = cast(AbsorbingElement, expression.token.components[AbsorbingElement]).element
    for argument in expression.arguments:
        value = cast(Value, argument.token.components[Value]).value
        if value == absorving_element:
            return Expression(Token({Value: Value("0"), Operand: Operand()}), [])

    return expression

def isolate_basic_operators(expression: Expression) -> Expression:
    if InverseComponents not in expression.token.components:
        return expression
    
    inverse_components = cast(InverseComponents, expression.token.components[InverseComponents]).components
    if BasicOperator not in inverse_components or ElementInverse not in inverse_components:
        return expression

    element_inverse = cast(ElementInverse, inverse_components[ElementInverse])

    simplified = Expression(Token(inverse_components), [])
    for argument in expression.arguments:
        simplified_argument = Expression(Token(element_inverse.operator_components), [argument, element_inverse.right_operand])
        simplified_argument = simplify_absorving_element(simplified_argument)
        simplified.arguments.append(simplified_argument)

    simplified.arguments[0] = expression.arguments[0]
    return simplified

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
    
    if UnaryIdentity in expression.token.components and len(expression.arguments) == 1:
        return expression.arguments[0]
    
    if (Operand in expression.token.components or
        Identity not in expression.token.components):

        return expression

    simplified_expressions: list[Expression] = []

    identity = cast(Identity, expression.token.components.get(Identity)).identity
    for argument in expression.arguments:
        value = cast(Value, argument.token.components[Value]).value

        if identity != value:
            simplified_expressions.append(argument)

    if not simplified_expressions:
        zero_token = Token({Value: Value("0"), Operand: Operand()})
        return Expression(zero_token, [])

    expression = Expression(expression.token, simplified_expressions)

    if len(simplified_expressions) == len(expression.arguments):
        return expression

    return simplify_identities(expression)

def simplify(expression: Expression) -> Expression:

    if not expression.arguments:
        return expression
    
    for index, argument in enumerate(expression.arguments):
        expression.arguments[index] = simplify(argument)

    expression = isolate_basic_operators(expression)
    expression = group_associatives(expression)
    expression = simplify_identities(expression)
        
    return expression

minus_one = Expression(Token({Value: Value("-1"), Operand: Operand()}), [])

operators: dict[str, dict[type, object]] = {
    "(": {OpenParenthesis: OpenParenthesis()},
    ")": {CloseParenthesis: CloseParenthesis()}
}

operators["^"] = {
    Value: Value("^"), 
    Operator: Operator(priority=3), 
    Associative: Associative()
}

operators["*"] = {
    Value: Value("*"),
    Operator: Operator(priority=2), 
    Associative: Associative(),
    BasicOperator: BasicOperator(),
    ElementInverse: ElementInverse(operators["^"], minus_one),
    UnaryIdentity: UnaryIdentity(),
    Identity: Identity("1"),
    AbsorbingElement: AbsorbingElement("0")
}

operators["/"] = {
    Value: Value("/"), 
    Operator: Operator(priority=2),
    InverseComponents: InverseComponents(operators["*"])
}

operators["+"] = {
    Value: Value("+"),
    Operator: Operator(priority=1),
    UnaryPrefix: UnaryPrefix(),
    Associative: Associative(),
    BasicOperator: BasicOperator(),
    ElementInverse: ElementInverse(operators["*"], minus_one),
    UnaryIdentity: UnaryIdentity(),
    Identity: Identity("0")
}

operators["-"] = {
    Value: Value("-"),
    Operator: Operator(priority=1),
    InverseComponents: InverseComponents(operators["+"]),
    UnaryPrefix: UnaryPrefix()
}

tokens = tokenize("1 +1 -0 + --2 --x", operators)

try:
    expression = parse(tokens)
    expression = simplify(expression)
    print(expression)
except ValueError as error:
    print(str(error))