from random import random

numbers = (int, float, complex)

class SmartExpression:
    op_string_dict = {
            '+':'+',
            '-':'-',
            '*':'\\cdot',
            '/':'\\over',
            '^':'^',
            '=':'='
        }

    def __init__(self, root, children=None, show_parentheses=False):
        self.root = root
        self.children = children if children else []
        self.show_parentheses = show_parentheses
        self.generate_stringlist() # sets self.stringlist and self.addressbook

    def generate_stringlist(self): # Currently only works for binary trees. What a knot this has been!
        """
        This method sets the value of self.stringlist, and also of self.addressbook,
        which is a dictionary whose keys are addresses of subexpressions,
        and whose values lists of indices of the stringlist corresponding to that subexpression.
        """

        # Helper functions
        def shift_list(L,i):
            return [l+i for l in L]
        def widen_list(L):
            return [L[0]-1] + L + [L[-1]+1]
        
        # Base case
        if not self.children:
            if self.show_parentheses:
                self.stringlist = ['\\left(', str(self.root), '\\right)']
                self.addressbook = {'':[0,1,2]}
            else:
                self.stringlist = [str(self.root)]
                self.addressbook = {'':[0]}
            return None
        
        # Must be binary for now
        if len(self.children)>2:
            pass
            #raise NotImplementedError
        
        # New stringlist
        self.stringlist = ['{'] + self.children[0].stringlist + ['}'] + [SmartExpression.op_string_dict[self.root]] + ['{'] + self.children[1].stringlist + ['}']
        if self.show_parentheses:
            self.stringlist = ['\\left('] + self.stringlist + ['\\right)']
        
        # New addressbook
        self.addressbook = {'':list(range(len(self.stringlist)))} # empty string should be entire expression
        for a in self.children[0].addressbook.keys(): # shift to new position
            self.addressbook['0'+a] = shift_list(self.children[0].addressbook[a],1+self.show_parentheses)
        self.addressbook['0'] = widen_list(self.addressbook['0']) # widen to include brackets
        for a in self.children[1].addressbook.keys(): # shift to new position
            self.addressbook['1'+a] = shift_list(self.children[1].addressbook[a],len(self.children[0].stringlist)+4+self.show_parentheses)
        self.addressbook['1'] = widen_list(self.addressbook['1']) # widen to include brackets

    def get_subex_at_address(self, address):
        # Retrieves the subexpression at the specified address within the SmartExpression tree.
        # Throws an IndexError if the address is not valid.
        if not address:
            return self  # Return original subexpression unchanged

        index = int(address[0])
        remaining_address = address[1:]

        if index >= len(self.children):
            raise IndexError(f"No child found at index {index}")

        return self.children[index].get_subex_at_address(remaining_address)

    def get_address_of_subex(self, subex):
        # Searches the tree of self recursively for a matching subexpression.
        # If one is found, returns the address of the match. Only finds one.
        # If one is not found, returns None
        if self == subex:
            return ""

        for i, child in enumerate(self.children):
            result = child.get_address_of_subex(subex)
            if result is not None:
                return str(i) + result

        return None

    def evaluate(self, vardict=None):
        if not self.children:  # Base case: leaf node
            if isinstance(self.root, numbers):
                return self.root  # Return number value
            elif vardict and self.root in vardict:  # Check if variable exists in vardict
                return vardict[self.root]  # Return variable value from vardict
            else:
                return self  # Return self if variable is not evaluated or not found in vardict

        # Evaluate children recursively
        evaluated_children = [child.evaluate(vardict) for child in self.children]

        # Check if all children are numbers
        if all(isinstance(child, numbers) or (isinstance(child, SmartExpression) and isinstance(child.root, numbers)) for child in evaluated_children):
            # Perform operation on numbers
            if self.root == "+":
                return sum(evaluated_children)
            elif self.root == "-":
                return evaluated_children[0] - evaluated_children[1]
            elif self.root == "*":
                result = evaluated_children[0]
                for child in evaluated_children[1:]:
                    result *= child
                return result
            elif self.root == "/":
                # Handling integer case so we don't get a float unnecessarily
                result = evaluated_children[0] / evaluated_children[1]
                if result % 1 == 0:
                    return int(result)
                else:
                    return result
            elif self.root == "^":
                return evaluated_children[0] ** evaluated_children[1]
            elif self.root == "=": # Should only be at the top level, in the case of an equation. Returns boolean
                return evaluated_children[0] == evaluated_children[1]

        return self  # Some children are not numbers

    def __str__(self):
        return "".join(self.stringlist)

    def __eq__(self, other):
        if isinstance(other, SmartExpression):
            return self.root == other.root and self.children == other.children
        elif isinstance(other, numbers):
            return self.__eq__(SmartExpression(other))
        return False

    def __add__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("+", [self, other])
        elif isinstance(other, numbers):
            return SmartExpression("+", [self, SmartExpression(other)])
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("+", [other, self])
        elif isinstance(other, numbers):
            return SmartExpression("+", [SmartExpression(other), self])
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("-", [self, other])
        elif isinstance(other, numbers):
            return SmartExpression("-", [self, SmartExpression(other)])
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("-", [other, self])
        elif isinstance(other, numbers):
            return SmartExpression("-", [SmartExpression(other), self])
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("*", [self, other])
        elif isinstance(other, numbers):
            return SmartExpression("*", [self, SmartExpression(other)])
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("*", [other, self])
        elif isinstance(other, numbers):
            return SmartExpression("*", [SmartExpression(other), self])
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("/", [self, other])
        elif isinstance(other, numbers):
            return SmartExpression("/", [self, SmartExpression(other)])
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("/", [other, self])
        elif isinstance(other, numbers):
            return SmartExpression("/", [SmartExpression(other), self])
        else:
            return NotImplemented

    def __xor__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("^", [self, other])
        elif isinstance(other, numbers):
            return SmartExpression("^", [self, SmartExpression(other)])
        else:
            return NotImplemented

    def __rxor__(self, other):
        if isinstance(other, SmartExpression):
            return SmartExpression("^", [other, self])
        elif isinstance(other, numbers):
            return SmartExpression("^", [SmartExpression(other), self])
        else:
            return NotImplemented

    def __pow__(self, other):
        return self.__xor__(other)

    def __rpow__(self, other):
        return self.__rxor__(other)

    def give_parentheses(self):
        self.show_parentheses = True
        self.generate_stringlist()
        return self

    def depth(self):
        return max(map(len,self.addressbook.keys()))

    def substitute_at_address(self, address, subex): #GPT
        if isinstance(subex, numbers):
            subex = SmartExpression(subex)

        if address == "":
            return subex

        index = int(address[0])
        remaining_address = address[1:]

        if index >= len(self.children):
            raise IndexError(f"No child found at index {index}")

        new_children = self.children.copy()
        new_children[index] = new_children[index].substitute_at_address(remaining_address, subex)

        return SmartExpression(self.root, children=new_children, show_parentheses=self.show_parentheses)

    def evaluate_at_address(self, address, vardict=None): #GPT
        if address == "":
            result = self.evaluate(vardict)
            if not isinstance(result, SmartExpression):
                result = SmartExpression(result)
            return result

        index = int(address[0])
        remaining_address = address[1:]

        if index >= len(self.children):
            raise IndexError(f"No child found at index {index}")

        new_child = self.children[index].evaluate_at_address(remaining_address, vardict)
        return self.substitute_at_address(address[0], new_child)

    def deepest_address(self):
        return [ad for ad in self.addressbook.keys() if len(ad) == self.depth()][0]

    def deepest_nonleaf_address(self):
        return self.deepest_address()[:-1]

    def evaluate_deepest_nonleaf(self):
        # Assumes expression contains no variables
        return self.evaluate_at_address(self.deepest_nonleaf_address())
    
    def get_all_leaves(self):
        if not self.children:  # Base case: leaf node
            return [self]
        all_leaves = []
        for child in self.children:
            all_leaves.extend(child.get_all_leaves())
        return all_leaves

    def get_all_variables(self):
        # Returns the set of variable strings present in the expression.
        # Note that it returns a set of strings, not a set of SmartExpressions.
        leaves = self.get_all_leaves()
        variables = set(leaf.root for leaf in leaves if not isinstance(leaf.root, numbers))
        return variables

    def test_equivalance_numerically(self, other, precision=1e-6, number_of_tests=5):
        variables_present = self.get_all_variables() | other.get_all_variables()
        variable_values = {var:100*random() for var in variables_present}
        for i in range(number_of_tests):
            if abs(self.evaluate(variable_values) - other.evaluate(variable_values)) > precision:
                return False
        return True

    def is_negative(self):
        # Currently only works for numbers... we need something better for negative signs like -x^3 or -3^2
        if isinstance(self.root, numbers):
            return self.root < 0
        else:
            return False

    def is_number(self):
        if isinstance(self, [int, float, complex]):
            return True
        elif isinstance(self, SmartExpression):
            if self.is_leaf():
                return is_number(self.root)
            else:
                return False
        elif isinstance(self, SmartTex):
            return is_number(self.SE)
        else:
            return False

    def set_pemdas_parentheses(self):
        # If spaghetti nightmare. Table of examples in Freeform
        if self.children:
            if self.root == '+':
                for i in range(0,len(self.children)):
                    if self.children[i].is_negative():
                        self.children[i].give_parentheses()
            elif self.root == '-':
                assert len(self.children) == 2
                if self.children[1].root in ['+','-'] or self.children[1].is_negative():
                    self.children[1].give_parentheses()
            elif self.root == '*':
                for i in range(0,len(self.children)):
                    if self.children[i].root in ['+','-'] or self.children[i].is_negative():
                        self.children[i].give_parentheses()
            elif self.root == '/':
                assert len(self.children) == 2
                pass
            elif self.root == '^':
                assert len(self.children) == 2
                if self.children[0].root in ['+','-','*','/','^'] or self.children[0].is_negative():
                    self.children[0].give_parentheses()
                # if self.children[1].root in ['^']: # I think I changed my mind,
                #     self.children[1].give_parentheses() # better without parentheses
            elif self.root == '=':
                assert len(self.children) == 2
                pass
            else:
                raise ValueError(f"Unknown operator {self.root}")
        for c in self.children:
            c.set_pemdas_parentheses()
        self.generate_stringlist()
        return self

    def get_evaluation_sequence(self, address_sequence=None, include_original=False):
        # Returns a list of SmartExpressions corresponding to its sequential evaluation at the given addresses.
        # Gets these addresses from somewhere else. Assumes no variables.
        if not address_sequence:
            address_sequence = self.get_address_sequence()
        Results = [self] if include_original else []
        current = self
        for address in address_sequence:
            new = current.evaluate_at_address(address)
            Results.append(new)
            current = new
        return Results

    def get_all_nonleaf_addresses(self):
        # Returns a set of addresses corresponding to all nonleaf nodes in the expression.
        all_addresses = list(self.addressbook.keys())
        all_addresses.remove("")
        return set([ad[:-1] for ad in all_addresses])

    def is_leaf(self):
        return not self.children

    def is_twig(self):
        return not is_leaf() and all([c.is_leaf() for c in self.children])

    def get_address_sequence(self, mode="left to right"):
        # Returns a list of addresses
        if mode == "left to right":
            # Returns the simplest left to right order, evaluating necessary subexpressions first
            result = []
            if self.is_leaf():
                return result
            else:
                for i,c in enumerate(self.children):
                    child_sequence = c.get_address_sequence(mode=mode)
                    for c_ad in child_sequence:
                        result.append(str(i)+c_ad)
                result.append("")
                return result
        elif mode == "deepest first":
            raise NotImplementedError
        else:
            raise NotImplementedError

    def swap_children_at_address(self, address=""):
        # Assumes two children at address. Defaults to root.
        subex = self.get_subex_at_address(address)
        assert len(subex.children) == 2
        new_subex = SmartExpression(subex.root, [subex.children[1], subex.children[0]])
        return self.substitute_at_address(address, new_subex)



