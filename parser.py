from tokenizer import Token, ValueType

def reverse_recording(tokens: list[Token]) -> list[Token]:

    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}

    result = []
    stack = []

    for token in tokens:

        if token.type in (ValueType.NUMBER, ValueType.VARIABLE):
            result.append(token)

        elif token.type == ValueType.FUNCTION:
            stack.append(token)

        elif token.type == ValueType.OPERATOR:
            operator = token.value
            while stack and stack[-1].type == ValueType.OPERATOR:
                top_op = stack[-1].value
                if ((operator != "^" and precedence[operator] <= precedence[top_op]) or
                        (operator == "^" and precedence[operator] < precedence[top_op])):
                    result.append(stack.pop())
                else:
                    break
            stack.append(token)

        elif token.type == ValueType.LEFTPAREN:
            stack.append(token)

        elif token.type == ValueType.RIGHTPAREN:
            while stack and stack[-1].type != ValueType.LEFTPAREN:
                result.append(stack.pop())
            if not stack:
                raise ValueError(f"Ошибка скобок в позиции {token.position}")
            stack.pop()
            if stack and stack[-1].type == ValueType.FUNCTION:
                result.append(stack.pop())

    while stack:
        if stack[-1].type == ValueType.LEFTPAREN:
            raise ValueError(f"Ошибка скобок в позиции {stack[-1].position}")
        result.append(stack.pop())

    return result
