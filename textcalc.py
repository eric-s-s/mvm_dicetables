"""a module to calculate text expressions with +-*/"""
from __future__ import division

import operator as op
import ast


def is_num(number):
    try:
        return isinstance(number, (int, long, float))
    except NameError:
        return isinstance(number, (int, float))


class TextCalculator(object):
    allowed_operations = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                          ast.FloorDiv: op.floordiv, ast.Div: op.truediv,
                          ast.Mod: op.mod, ast.UAdd: op.pos, ast.USub: op.neg,
                          ast.BitXor: op.pow, ast.Pow: op.pow}

    exclusions = {'+': ast.Add, '-': ast.Sub, '*': ast.Mult, '/': ast.Div,
                  '//': ast.FloorDiv, '**': ast.Pow, '^': ast.BitXor, '%': ast.Mod}

    def __init__(self, exclusion_list=None):
        """

        :param exclusion_list: accepted elements\n
            '+', '-', '*', '/', '//', '**', '^'
        """
        self.excluded_funcs = []
        if exclusion_list is None:
            exclusion_list = []
        for operator in exclusion_list:
            self.excluded_funcs.append(self.exclusions[operator])

        self._max_val = 1e+100
        self._max_str_len = 50

    @property
    def max_val(self):
        return self._max_val

    @max_val.setter
    def max_val(self, number):
        if is_num(number):
            self._max_val = number

    @property
    def max_str_len(self):
        return self._max_str_len

    @max_str_len.setter
    def max_str_len(self, number):
        if is_num(number):
            self._max_str_len = number

    def check_excluded(self, node):
        if type(node.op) in self.excluded_funcs:
            raise KeyError(type(node.op))

    def check_length(self, equation):
        if len(equation) > self.max_str_len:
            raise SyntaxError('line too long: max {}'.format(self.max_str_len))

    def check_answer(self, number):
        if number > self.max_val:
            raise ValueError('answer is larger than max value: {}'.format(self.max_val))

    @staticmethod
    def _get_nodes(equation):
        should_be_expr = ast.parse(equation).body[0]
        if not isinstance(should_be_expr, ast.Expr):
            raise SyntaxError('not an expression')
        return should_be_expr.value

    def _node_eval(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.UnaryOp):
            return self.allowed_operations[type(node.op)](self._node_eval(node.operand))
        elif isinstance(node, ast.BinOp):
            self.check_excluded(node)
            return self.allowed_operations[type(node.op)](self._node_eval(node.left),
                                                          self._node_eval(node.right))
        else:
            raise SyntaxError('did not understand value or operator: {}'
                              .format(get_ast_class_name(str(type(node)))))

    def eval_equation(self, expr):
        try:
            return self._node_eval(self._get_nodes(expr))
        except KeyError as error:
            func_name = get_func_name(error)
            raise SyntaxError('{} operation not allowed'.format(func_name))

    def safe_eval(self, expr):
        """

        :param expr: string
        :return: (number, error message)
        """
        if not expr:
            return 0, 'None'
        try:
            self.check_length(expr)
            ans = self.eval_equation(expr)
            self.check_answer(ans)
            return ans, 'ok'
        except (SyntaxError, ZeroDivisionError, OverflowError, ValueError) as error:
            return 0, str(error)


def get_func_name(error):
    func_name = get_ast_class_name(str(error))
    # ast evals '^' to BitXor and TextCalculator evals '^' to Pow
    if func_name == "<BitXor>":
        func_name = "<Pow>"
    return func_name


def get_ast_class_name(type_str):
    out = type_str.replace("<class '_ast.", "<")
    out = out.replace("'>", ">")
    return out


def safe_eval(expr, *excluded, **kwargs):
    """

    :param expr: str of math expr using numbers\n
        and + - * / () ^ ** // %
    :param excluded: can be '+', '-', '*', '/',\n
        '//', '**', '^', '%'
    :param kwargs: max_val, max_str_len
    :return: (ans, 'ok'), (0, 'None')\n
        or (0, 'error message')
    """
    calculator = TextCalculator(list(excluded))
    for key, value in kwargs.items():
        setattr(calculator, key, value)
    return calculator.safe_eval(expr)
