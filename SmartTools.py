from SmartExpressions import *
from ManimIntegration import *
import random

SmE = SmartExpression
SmT = SmartTex

x = SmE('x')
x2 = x^2
x3 = x^3
x4 = x^4
y = SmE('y')
y2 = y^2
y3 = y^3
y4 = y^4
z = SmE('z')
z2 = z^2
z3 = z^3
z4 = z^4
a = SmE('a')
b = SmE('b')
c = SmE('c')


# Helpful printing tools for bugfixing
def clearprint(SE, mode="addressbook"):
    if isinstance(SE, SmartTex):
        SE = SE.SE
    print("----")
    if mode == "stringlist":
        print(f"Stringlist for {SE}:")
        for i,S in enumerate(SE.stringlist):
            print(f"{i:5}:   {S}")
    elif mode == "addressbook":
        print(f"Addressbook and strings for {SE}:")
        for ad,indices in SE.addressbook.items():
            stringsection = "".join([SE.stringlist[i] for i in indices])
            print(f"{ad:5}:   {stringsection}")


def random_number_expression(max_depth=2, number_list=range(0,13), op_list=['+','-','*','/','^']):
    if max_depth == 0 or random.random() < 1/max_depth:
        return SmE(random.choice(number_list))
    else:
        return SmE(random.choice(op_list), [random_number_expression(max_depth-1, number_list, op_list), random_number_expression(max_depth-1, number_list, op_list)])



def random_pemdas_expression(max_depth=3, number_list=range(0, 13), op_list=['+', '-', '*', '/', '^'], integers_only=True, max_value=1000):
    if max_depth == 0 or (integers_only and max_value < 1):
        # Reached maximum depth or maximum value constraint, return a random number
        return SmE(random.choice(number_list))

    # Randomly select an operation
    operation = random.choice(op_list)

    # Generate left and right subexpressions recursively
    while True:
        left = random_pemdas_expression(max_depth - 1, number_list, op_list, integers_only, max_value)
        right = random_pemdas_expression(max_depth - 1, number_list, op_list, integers_only, max_value)

        Result = SmE(operation,[left,right])
        if integers_only:
            try:
                result = Result.evaluate()
                if isinstance(result, int) and abs(result) < max_value:
                    # Valid result obtained, break the loop
                    break
            except (ZeroDivisionError, TypeError):
                # Handle division by zero or type errors
                pass
        else:
            break

    Result.set_pemdas_parentheses()
    return Result



