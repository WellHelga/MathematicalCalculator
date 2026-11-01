import math
from tokenizer import Token, ValueType
from tree import TreeNode

MATH_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "cot": lambda x: math.cos(x) / math.sin(x) if abs(math.sin(x)) > 1e-10 else float("inf"),
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "abs": abs,
}

MATH_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}

def find_variables(expr: str) -> set:

    from tokenizer import tokenize

    try:
        tokens = tokenize(expr)
        return {t.value for t in tokens if t.type.value == "VARIABLE" and t.value in ("x", "y")}
    except:
        return set()

def calculator_tree(node: TreeNode, variables: dict = None) -> float:

    if variables is None:
        variables = {}

    token = node.token

    if token.type == ValueType.NUMBER:
        return token.value

    if token.type == ValueType.VARIABLE:
        if token.value in variables:
            return variables[token.value]
        elif token.value in MATH_CONSTANTS:
            return MATH_CONSTANTS[token.value]
        else:
            raise ValueError(f"ошибка в позиции {token.position}: неизвестная переменная {token.value}")

    if token.type == ValueType.FUNCTION:
        arg = calculator_tree(node.left, variables)
        if token.value not in MATH_FUNCTIONS:
            raise ValueError(f"ошибка в позиции {token.position}: неизвестная функция {token.value}")
        try:
            return MATH_FUNCTIONS[token.value](arg)
        except ValueError as e:
            raise ValueError(f"ошибка в позиции {token.position}: {e}")

    if token.type == ValueType.OPERATOR:
        left_val = calculator_tree(node.left, variables)
        right_val = calculator_tree(node.right, variables)

        if token.value == "+":
            return left_val + right_val
        elif token.value == "-":
            return left_val - right_val
        elif token.value == "*":
            return left_val * right_val
        elif token.value == "/":
            if right_val == 0:
                raise ZeroDivisionError(f"ошибка в позиции {token.position}: деление на ноль")
            return left_val / right_val
        elif token.value == "^":
            return left_val ** right_val

    raise ValueError(f"ошибка в позиции {token.position}")

def calculator_expr(expr: str, x_value: float = None, y_value: float = None, **kwargs) -> float:

    from tokenizer import tokenize
    from parser import reverse_recording
    from tree import tree

    tokens = tokenize(expr)
    rpn = reverse_recording(tokens)
    tree = tree(rpn)

    variables = {}
    if x_value is not None:
        variables["x"] = x_value
    if y_value is not None:
        variables["y"] = y_value
    variables.update(kwargs)

    return calculator_tree(tree, variables)