from manim import *
from SmartExpressions import *
import copy


class SmartTex(MathTex):
    def __init__(self, smart_expression, auto_paren=True, **kwargs):
        if not isinstance(smart_expression, SmartExpression):
            try:
                smart_expression = SmartExpression(smart_expression)
            except:
                raise ValueError("smart_expression must be an instance of SmartExpression")
        self.SE = smart_expression
        self.joined_version = MathTex(" ".join(smart_expression.stringlist))
        if auto_paren:
            self.SE.set_pemdas_parentheses()
        stringlist = smart_expression.stringlist
        super().__init__(*stringlist, **kwargs)
    
    def __getitem__(self, key):
        # Returns the VGroup of submobjects corresponding to the indices in the addressbook for the given address
        if isinstance(key, int):
            return super().__getitem__(key)
        elif isinstance(key, str):
            indices = self.SE.addressbook[key]
            return VGroup(*[self[i] for i in indices])
    
    def __add__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(self.SE + other.SE)
        else:
            try:
                return SmartTex(self.SE + other)
            except:
                return NotImplemented
    
    def __radd__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(other.SE + self.SE)
        else:
            try:
                return SmartTex(other + self.SE)
            except:
                return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(self.SE - other.SE)
        else:
            try:
                return SmartTex(self.SE - other)
            except:
                return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(other.SE - self.SE)
        else:
            try:
                return SmartTex(other - self.SE)
            except:
                return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(self.SE * other.SE)
        else:
            try:
                return SmartTex(self.SE * other)
            except:
                return NotImplemented
    
    def __rmul__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(other.SE * self.SE)
        else:
            try:
                return SmartTex(other * self.SE)
            except:
                return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(self.SE / other.SE)
        else:
            try:
                return SmartTex(self.SE / other)
            except:
                return NotImplemented
    
    def __rtruediv__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(other.SE / self.SE)
        else:
            try:
                return SmartTex(other / self.SE)
            except:
                return NotImplemented
    
    def __xor__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(self.SE ^ other.SE)
        else:
            try:
                return SmartTex(self.SE ^ other)
            except:
                return NotImplemented
    
    def __rxor__(self, other):
        if isinstance(other, SmartTex):
            return SmartTex(other.SE ^ self.SE)
        else:
            try:
                return SmartTex(other ^ self.SE)
            except:
                return NotImplemented
    
    def __pow__(self, other):
        return self.__xor__(other)
    
    def __rpow__(self, other):
        return self.__rxor__(other)

    def Create_bugless(self, scene):
        # Used in place of Create because this sometimes is bugged for these
        # Called in a Scene with A.Create_bugless(self)
        spoof = MathTex(" ".join(self.SE.stringlist))
        scene.play(Create(spoof))
        scene.remove(spoof)
        scene.add(self)

def remove_sublist(lst, sublist): # Helper function
    return [element for element in lst if element not in sublist]

def get_glyphs(mobjs): # Helper function from Abulafia on Discord
    return [c for g in mobjs for c in g if not isinstance(c, VectorizedPoint)]

def SmartTransform(A,B,construction_address="",**kwargs):
    return AnimationGroup(
        Transform(
                VGroup(*get_glyphs([A[i] for i in A.SE.addressbook[construction_address]])),
                VGroup(*get_glyphs([B[i] for i in B.SE.addressbook[construction_address]]))
                ),
        *[
            Transform(A[i],B[j])
            for i,j in zip(
                remove_sublist(A.SE.addressbook[""],A.SE.addressbook[construction_address]),
                remove_sublist(B.SE.addressbook[""],B.SE.addressbook[construction_address])
            )
        ],
            **kwargs
    )

def EvaluateInPlace(A, anim_time=1, wait_time=0.5, evaluation_order="left to right"):
    A_sequence = [A]
    address_sequence = A.SE.get_address_sequence(evaluation_order)
    evaluation_sequence = A.SE.get_evaluation_sequence(address_sequence)
    A_sequence = A_sequence + list(map(SmartTex,evaluation_sequence))
    return Succession(
        *[
            SmartTransform(A, A_sequence[n+1], address_sequence[n], run_time=anim_time)
            for n in range(len(evaluation_sequence))
        ],
        lag_ratio = (anim_time + wait_time) / anim_time
    )

def SwapChildren(A, address, scene, **kwargs):
    # Transforms children of subexpression into each other.
    # Good for commutativity or reciprocals.
    # Assumes two children.
    # Does not work more than once in a row! Idk what I'm doing now
    print(scene.mobjects)
    subex = A.SE.get_subex_at_address(address)
    assert len(subex.children) == 2
    new_SE = copy.deepcopy(A.SE)
    new_SE = new_SE.substitute_at_address(address + "0", subex.children[1])
    new_SE = new_SE.substitute_at_address(address + "1", subex.children[0])
    B = SmartTex(new_SE)
    #print(scene.mobjects)
    scene.play(AnimationGroup(
        ReplacementTransform(
            VGroup(*get_glyphs([A[i] for i in A.SE.addressbook[address + "0"]])),
            VGroup(*get_glyphs([B[i] for i in B.SE.addressbook[address + "1"]]))
            ),
        ReplacementTransform(
            VGroup(*get_glyphs([A[i] for i in A.SE.addressbook[address + "1"]])),
            VGroup(*get_glyphs([B[i] for i in B.SE.addressbook[address + "0"]]))
            ),
        *[
            ReplacementTransform(A[i],B[j])
            for i,j in zip(
                remove_sublist(A.SE.addressbook[""], A.SE.addressbook[address + "0"] + A.SE.addressbook[address + "1"]),
                remove_sublist(B.SE.addressbook[""], B.SE.addressbook[address + "0"] + B.SE.addressbook[address + "1"])
            )
        ],
            **kwargs
    ))
    #print(scene.mobjects)
    #print(A in scene.mobjects)
    #B.replace(A)
    scene.remove(A,B)


