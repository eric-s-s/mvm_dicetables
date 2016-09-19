"""a module to calculate text expressions with +-*/"""
from __future__ import division

from operator import add, mul, truediv, sub, pos, neg, floordiv
import ast


class TextEvaluator(object):
    allowed_operations = {ast.Add: add, ast.Sub: sub, ast.Mult: mul,
                          ast.FloorDiv: floordiv, ast.Div: truediv,
                          ast.UAdd: pos, ast.USub: neg,
                          ast.BitXor: pow, ast.Pow: pow}

    exclusions = {'+': ast.Add, '-': ast.Sub, '*': ast.Mult, '/': ast.Div,
                  '//': ast.FloorDiv, '**': ast.Pow, '^': ast.BitXor}

    def __init__(self, exclusion_list=None):
        self.excluded_funcs = []
        if exclusion_list is None:
            exclusion_list = []
        for operator in exclusion_list:
            self.excluded_funcs.append(self.exclusions[operator])

    def check_excluded(self, node):
        if type(node.op) in self.excluded_funcs:
            raise KeyError(type(node.op))

    @staticmethod
    def check_length(equation):
        max_len = 50
        if len(equation) > max_len:
            raise SyntaxError('line too long: max {}'.format(max_len))

    @staticmethod
    def check_answer(number):
        max_val = 1.0e+100
        if number > max_val:
            raise ValueError('answer larger than max allowed: {}'.format(max_val))

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
        try:
            self.check_length(expr)
            ans = self.eval_equation(expr)
            self.check_answer(ans)
            return ans, 'ok'
        except (SyntaxError, ZeroDivisionError, OverflowError, ValueError) as error:
            return 0, str(error)


def get_func_name(error):
    func_name = get_ast_class_name(str(error))
    if func_name == "<BitXor>":
        func_name = "<Pow>"
    return func_name


def get_ast_class_name(type_str):
    out = type_str.replace("<class '_ast.", "<")
    out = out.replace("'>", ">")
    return out


def safe_eval(expr, *excluded):
    """

    :param expr: str of math expr using numbers\n
        and + - * / () ^ ** //
    :param excluded: can be '+', '-', '*', '/',\n
        '//', '**', '^'
    :return: (ans, 'ok') or (0, 'error message')
    """
    doer = TextEvaluator(list(excluded))
    return doer.safe_eval(expr)



