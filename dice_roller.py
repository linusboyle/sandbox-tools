from lark import Lark, Transformer
from heapq_util import max_n, min_n
import random
import argparse

# Grammar for parsing dice expressions
dice_grammar = r"""
    start : expression
    expression : term ((ADD | SUB) expression)?
    term : factor ((MUL | DIV) term)?
    factor : dice | constant | "(" expression ")"

    dice : (simpledice | dicepool) modifiers          # type int
    simpledice: expression "d" expression
    dicepool : "{" dicelist "}"  # type list
    dicelist : dice ("," dicelist)?       # type list

    modifiers : | modifier modifiers
    modifier : kh | kl | dh | dl | min | max #type func: list -> list
    kh: "kh" constant?
    kl: "kl" constant?
    dh: "dh" constant?
    dl: "dl" constant?
    min: "min" constant?
    max: "max" constant?

    constant : NUMBER

    ADD: "+"
    SUB: "-"
    MUL: "*"
    DIV: "/"
    NUMBER: /\d+/
    %ignore " "
"""

class DiceTransformer(Transformer):

    def __init__(self):
        self.rolls = {}

    def start(self, args):
        return args[0]

    def expression(self, args):
        if len(args) == 1:
            return args[0]
        left = args[0]
        op = args[1]
        right = args[2]
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        return left

    def term(self, args):
        if len(args) == 1:
            return args[0]
        left = args[0]
        op = args[1]
        right = args[2]
        if op == '*':
            return left * right
        elif op == '/':
            return left // right
        return left

    def factor(self, args):
        if len(args) == 3:
            return args[1]
        return args[0]

    def dice(self, args):
        pool = args[0]
        if len(args) == 2:
            modifier = args[1]
        else:
            modifier = lambda x : x
        return sum(modifier(pool))

    def simpledice(self, args):
        count = args[0]
        sides = args[1]

        if count <= 0 or sides <= 0:
            result = []
        else:
            result = [random.randint(1, sides) for _ in range(count)]
        self.rolls[f"{count}d{sides}"] = result
        return result;

    def dicelist(self, args):
        if len(args) == 1:
            return args
        else:
            return [args[0], *args[1]]

    def dicepool(self, args):
        pool = args[0]
        return pool

    def constant(self, args):
        return int(args[0])

    def modifiers(self, args):
        if len(args) == 0:
            return lambda x : x
        else:
            f = args[0]
            g = args[1]
            return lambda x : g(f(x))

    def modifier(self, args):
        return args[0]
    
    def kh(self, args):
        if len(args) == 0:
            length = 1
        else:
            length = args[0]
        return lambda x : max_n(x, length)
   
    def kl(self, args):
        if len(args) == 0:
            length = 1
        else:
            length = args[0]
        return lambda x : min_n(x, length)

    def dh(self, args):
        if len(args) == 0:
            length = 1
        else:
            length = args[0]
        return lambda x : min_n(x, len(x) - length)

    def dl(self, args):
        if len(args) == 0:
            length = 1
        else:
            length = args[0]
        return lambda x : max_n(x, len(x) - length)
    
    def min(self, args):
        if len(args) == 0:
            return lambda x : x
        minimum = args[0]
        def replace_min(x):
            return [minimum if i < minimum else i for i in x]
        return replace_min

    def max(self, args):
        if len(args) == 0:
            return lambda x : x
        maximum = args[0]
        def replace_max(x):
            return [maximum if i > maximum else i for i in x]
        return replace_max

def roll_formula(formula):
    """
    Parses and evaluates a dice formula.
    
    Args:
        formula (str): The dice formula to roll.
    
    Returns:
        dict: A dictionary containing the result of the roll and the individual rolls.
    """
    parser = Lark(dice_grammar)
    tree = parser.parse(formula)
    # print(tree.pretty())
    # print(tree)
    transformer = DiceTransformer()
    result = transformer.transform(tree)
    return {
        "result": result, # integer result
        "rolls": transformer.rolls, # dice roll of simple dice formulas
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Roll dice using a formula.")
    parser.add_argument("formula", type=str, help="The dice formula to roll (e.g., 2d6+3, 10d12kh3, 5d12min3, {1d12, 2d10, 5d6}dl)")
    args = parser.parse_args()

    try:
        result = roll_formula(args.formula)
        print(f"Formula: {args.formula}")
        print(f"Result: {result["result"]}")
        print(f"Rolls: {result["rolls"]}")
    except Exception as e:
        print(f"Error parsing formula: {args.formula}")
        print(str(e))