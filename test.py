from tokenizer import tokenize
from parser import reverse_recording
from tree import tree
from calculator import calculator_expr

tokens = tokenize("3 + 3 * 10")
opz = reverse_recording(tokens)
print([x.value for x in opz])

tokens = tokenize("(3 + 10) ^ 3 * (12 - pi)")
opz = reverse_recording(tokens)
print([x.value for x in opz])

tokens = tokenize("cos(20) / sin(10)")
opz = reverse_recording(tokens)
print([x.value for x in opz])

tokens = tokenize("log10(300)")
opz = reverse_recording(tokens)
print([x.value for x in opz])



result = calculator_expr("-5 + 3")
print(result)

result = calculator_expr("-x", x_value=5)
print(result)

result = calculator_expr("sin(-pi/2)")
print(result)



result = calculator_expr("3 + 3 * 10")
print(result)

result = calculator_expr("sin(pi/2)")
print(result)

result = calculator_expr("x^2 + 12", x_value=3)
print(result)



try:
    calculator_expr("12 / 0")
    print("исключение не выброшено")
except ZeroDivisionError as e:
    print(f"ошибка: {e}")

try:
    tokenize("3 + ,")
    print("исключение не выброшено")
except ValueError as e:
    print(f"ошибка: {e}")

try:
    tokenize("(6 * 2")
    reverse_recording(tokenize("(3 + 4"))
    print("исключение не выброшено")
except ValueError as e:
    print(f"ошибка: {e}")