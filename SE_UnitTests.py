from SmartExpressions import *
from SmartTools import * 

def test_smart_expression():
    # Create SmartExpressions
    A = SmartExpression("x")
    B = SmartExpression(5)
    C = A + B
    D = B - SmartExpression(3)
    E = D * SmartExpression(2)
    F = E / SmartExpression(4)
    G = F ^ SmartExpression(2)
    # for S in [A,B,C,D,E,F,G]:
    #     print(S)

    # Evaluate SmartExpressions
    assert A.evaluate() == A  # Variable x is not evaluated
    assert B.evaluate() == 5
    assert C.evaluate() == C  # Variable x is not evaluated
    assert C.evaluate({"x":12}) == 17
    assert C.evaluate({"z":12}) == C
    assert D.evaluate() == 2
    assert E.evaluate() == 4
    assert F.evaluate() == 1
    assert G.evaluate() == 1

    # Get LaTeX stringlist representation
    assert A.stringlist == ['x']
    assert B.stringlist == ['5']
    assert C.stringlist == ['{', 'x', '}', '+', '{', '5', '}']
    assert D.stringlist == ['{', '5', '}', '-', '{', '3', '}']
    assert E.stringlist == ['{', '{', '5', '}', '-', '{', '3', '}', '}', '\\cdot', '{', '2', '}']
    assert F.stringlist == ['{', '{', '{', '5', '}', '-', '{', '3', '}', '}', '\\cdot', '{', '2', '}', '}', '\\over', '{', '4', '}']
    assert G.stringlist == ['{', '{', '{', '{', '5', '}', '-', '{', '3', '}', '}', '\\cdot', '{', '2', '}', '}', '\\over', '{', '4', '}', '}', '^', '{', '2', '}']

    # Test string representation
    assert str(A) == "x"
    assert str(B) == "5"
    assert str(C) == "{x}+{5}"
    C.give_parentheses()
    assert str(C) == "\\left({x}+{5}\\right)"

    # Test get_subex_at_address
    expr = SmartExpression("+", [
        SmartExpression("*", [SmartExpression(2), SmartExpression(3)]),
        SmartExpression("-", [SmartExpression(5), SmartExpression(4)]),
    ])
    
    assert expr.get_subex_at_address("") == expr
    assert expr.get_subex_at_address("0") == SmE(2)*SmE(3)
    assert expr.get_subex_at_address("1") == SmE(5)-SmE(4)
    assert expr.get_subex_at_address("00") == SmE(2)
    assert expr.get_subex_at_address("01") == SmE(3)
    assert expr.get_subex_at_address("10") == SmE(5)
    assert expr.get_subex_at_address("11") == SmE(4)

    # Test retrieving subexpressions at different addresses
    assert expr.get_subex_at_address("") == expr
    assert expr.get_subex_at_address("0") == SmartExpression("*", [SmartExpression(2), SmartExpression(3)])
    assert expr.get_subex_at_address("1") == SmartExpression("-", [SmartExpression(5), SmartExpression(4)])
    assert expr.get_subex_at_address("00") == SmartExpression(2)
    assert expr.get_subex_at_address("01") == SmartExpression(3)
    assert expr.get_subex_at_address("10") == SmartExpression(5)
    assert expr.get_subex_at_address("11") == SmartExpression(4)
    try: # Test invalid address
        expr.get_subex_at_address("12")
    except IndexError:
        pass
    else:
        raise AssertionError("Expected IndexError")
    
    # Note that assigning a new SmartExpression to the result of
    # A.get_subex_at_address() does not substitute it into A.
    

    # Test finding addresses of subexpressions
    assert A.get_address_of_subex(A) == ""
    assert C.get_address_of_subex(A) == "0"
    assert G.get_address_of_subex(D) == "000"
    # Test get_address_of_subex with valid subexpressions
    expr = SmartExpression("*", [
        SmartExpression(2),
        SmartExpression("+", [
            SmartExpression(3),
            SmartExpression("x")
        ])
    ])
    assert expr.get_address_of_subex(SmartExpression(3)) == "10"
    assert expr.get_address_of_subex(SmartExpression("x")) == "11"
    assert expr.get_address_of_subex(SmartExpression("+", [
        SmartExpression(3),
        SmartExpression("x")
    ])) == "1"

    # Test get_address_of_subex with invalid subexpressions
    assert expr.get_address_of_subex(SmartExpression(2)) == "0"
    assert expr.get_address_of_subex(SmartExpression("+", [
        SmartExpression(3),
        SmartExpression(4)
    ])) is None
    

    # Test addressbook
    x = SmE('x')
    assert x.addressbook == {'':[0]}
    assert (x+5).addressbook == {
        '':[0,1,2,3,4,5,6],
        '0':[0,1,2],
        '1':[4,5,6]
    }
    assert (SmE(15) + SmE(2)*SmE(8)).addressbook == {
        '':[0,1,2,3,4,5,6,7,8,9,10,11,12],
        '0':[0,1,2],
        '1':[4,5,6,7,8,9,10,11,12],
        '10':[5,6,7],
        '11':[9,10,11]
        }


    # Test substitution at address
    A = (x+3)*(x2-5)
    assert A.substitute_at_address("",y) == y
    assert A.substitute_at_address("0",y) == y*(x2-5)
    assert A.substitute_at_address("1",y) == (x+3)*y
    assert A.substitute_at_address("100",y) == (x+3)*(y**2-5)
    assert A.substitute_at_address("101",y) == (x+3)*(x**y-5)
    assert A.substitute_at_address("101",y+z) == (x+3)*(x**(y+z)-5)
    assert A.substitute_at_address("101",6+z*y) == (x+3)*(x**(6+z*y)-5)
    assert A.substitute_at_address("00",4) == (SmE(4)+3)*(x2-5)
    A = A.substitute_at_address("100",3)
    assert A == (x+3)*(SmE(3)**2-5)
    assert A.substitute_at_address("10",9) == (x+3)*(SmE(9)-5)
    assert (SmE(3)**2-5).substitute_at_address("0",SmE(9)) == SmE(9)-5
    assert (SmE(3)**2-5).substitute_at_address("0",9) == SmE(9)-5
    assert (SmE(3)**2-5).evaluate_at_address("0",9) == SmE(9)-5


    # Test evaluate at address
    A = (x+3)/(SmE(3)**2-5)
    # print(A)
    # for ad in A.addressbook.keys():
    #     print(ad, A.evaluate_at_address(ad))
    assert A.evaluate_at_address("0",{"x":1}) == 4/(SmE(3)**2-5)
    assert A.evaluate_at_address("1") == (x+3)/SmE(4)
    assert A.evaluate_at_address("10") == (x+3)/(SmE(9)-5)
    

    # Test deepest address and evaluation
    assert A.deepest_address() == "100"
    assert A.deepest_nonleaf_address() == "10"
    assert A.evaluate_deepest_nonleaf() == (x+3)/(SmE(9)-5)
    A = A.evaluate_deepest_nonleaf().substitute_at_address("00",3)
    assert A.evaluate_deepest_nonleaf() == 6/(SmE(9)-5)
    A = A.evaluate_deepest_nonleaf()
    assert A.evaluate_deepest_nonleaf() == SmE(6)/4
    A = A.evaluate_deepest_nonleaf()
    assert A.evaluate_deepest_nonleaf() == SmE(1.5)
    A = A.evaluate_deepest_nonleaf()
    assert A == SmE(1.5)
    assert A == 1.5


    # B = ((SmE(1)+SmE(2)*3)**2-SmE(3)**2)/(SmE(2)*2+SmE(14)**0)
    # result = B.evaluate()
    # while B != result:
    #     print(B)
    #     B = B.evaluate_deepest_nonleaf()
    # print(B)


    # Test get all leaves
    C = (x2+3)/(y/z + SmE(8)/10)
    assert C.get_all_leaves() == [
        x,
        SmE(2),
        SmE(3),
        y,
        z,
        SmE(8),
        SmE(10)
    ]


    # Test get all variables
    assert C.get_all_variables() == {'x','y','z'}
    assert ((x*y*x)^8).get_all_variables() == {'x','y'}


    # Test test equivalence numerically vs equivalence
    Short = (x+y)**3
    Long = x**3 + 3*x**2*y + 3*x*y**2 + y**3
    assert not Short == Long
    assert Short.test_equivalance_numerically(Long)
    assert not Short.test_equivalance_numerically(Long+1)
    assert Short.test_equivalance_numerically(Long+0.000000001)
    A = x*y*z
    B = z*x*y
    assert not A == B
    assert A.test_equivalance_numerically(B)
    A = x+y+z-z-y
    B = x
    assert not A == B
    assert A.test_equivalance_numerically(B)
    assert not A.test_equivalance_numerically(B**3)

    # Test swap children at address
    A = SmE(3)+4
    assert A.swap_children_at_address() == SmE(4)+3
    B = (SmE(4)/2 + 8)*(SmE(3)-SmE(8)/5)
    assert B.swap_children_at_address("00") == (SmE(2)/4 + 8)*(SmE(3)-SmE(8)/5)
    assert B.swap_children_at_address("11") == (SmE(4)/2 + 8)*(SmE(3)-SmE(5)/8)
    C = SmE(3)/8
    assert A.swap_children_at_address().test_equivalance_numerically(A)
    assert not C.swap_children_at_address().test_equivalance_numerically(C)


    print("All tests pass!")


test_smart_expression()







