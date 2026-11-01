from enum import Enum

class ValueType(Enum):

    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    VARIABLE = "VARIABLE"
    FUNCTION = "FUNCTION"
    LEFTPAREN = "LEFTPAREN"
    RIGHTPAREN = "RIGHTPAREN"

class Token:

    def __init__(self, type: ValueType, value, position: int):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type.value}, {self.value}, position={self.position})"

FUNCTIONS = {"sin", "cos", "tan", "cot", "log", "log10", "sqrt", "exp", "abs"}


def unary_minus(expr: str, i: int) -> bool:

    if i == 0:
        return True
    j = i - 1
    while j >= 0 and expr[j] == " ":
        j -= 1
    if j < 0:
        return True

    return expr[j] in "(+-*/^"


def processing(expr: str) -> str:

    result = []
    for i, char in enumerate(expr):
        if char == "-" and unary_minus(expr, i):
            result.append("0")
        result.append(char)

    return "".join(result)

def tokenize(expr: str) -> list[Token]:

    expr = processing(expr)
    tokens = []
    i = 0
    length = len(expr)

    while i < length:
        char = expr[i]

        if char == " ":
            i += 1
            continue

        if char.isdigit() or char == ".":
            j = i
            while j < length and (expr[j].isdigit() or expr[j] == "."):
                j += 1
            tokens.append(Token(ValueType.NUMBER, float(expr[i:j]), i))
            i = j
            continue

        if char.isalpha():
            j = i
            while j < length and expr[j].isalpha():
                j += 1
            while j < length and expr[j].isdigit():
                j += 1
            word = expr[i:j]
            if word in FUNCTIONS:
                tokens.append(Token(ValueType.FUNCTION, word, i))
            elif word in ("pi", "e", "x", "y"):
                tokens.append(Token(ValueType.VARIABLE, word, i))
            else:
                raise ValueError(f"Неизвестное слово: {word} в позиции {i}")
            i = j
            continue

        if char == "(":
            tokens.append(Token(ValueType.LEFTPAREN, "(", i))
            i += 1
            continue

        if char == ")":
            tokens.append(Token(ValueType.RIGHTPAREN, ")", i))
            i += 1
            continue

        if char in "+-*/^":
            tokens.append(Token(ValueType.OPERATOR, char, i))
            i += 1
            continue

        raise ValueError(f"Неизвестный символ: {char} в позиции {i}")
    return tokens

if __name__ == "__main__":
    print(tokenize("sin(30) * cos(10)"))