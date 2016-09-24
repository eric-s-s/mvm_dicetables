"""test for calculate_text"""

import unittest
import ast

import textcalc as tc


def node(equation_string):
    return ast.parse(equation_string).body[0].value


class TestTextCalc(unittest.TestCase):
    def setUp(self):
        self.TC = tc.TextCalculator()
        self.TC_no_minus = tc.TextCalculator(['-'])

    def tearDown(self):
        del self.TC
        del self.TC_no_minus

    def check_safe_eval(self, equation, value, message, *exclusions, **kwargs):
        self.assertEqual(tc.safe_eval(equation, *exclusions, **kwargs), (value, message))

    def my_regex(self, error_type, regex, func, *args):
        with self.assertRaises(error_type) as cm:
            func(*args)
        error_msg = str(cm.exception)
        self.assertEqual(error_msg, regex)

    def test_my_regex(self):
        self.my_regex(ValueError, "invalid literal for int() with base 10: 'a'", int, 'a')

    def test_is_num(self):
        self.assertTrue(tc.is_num(10**1000))
        self.assertTrue(tc.is_num(2.5))
        self.assertFalse(tc.is_num('a'))

    def test_TextCalculator___init__(self):
        new = tc.TextCalculator(['+', '*'])
        self.assertEqual(new.excluded_funcs, [ast.Add, ast.Mult])

    def test_TextCalculator_max_val_get(self):
        self.assertEqual(self.TC.max_val, 1e+100)

    def test_TextCalculator_max_val_set_fail(self):
        self.TC.max_val = 'a'
        self.assertEqual(self.TC.max_val, 1e+100)

    def test_TextCalculator_max_val_set_pass(self):
        self.TC.max_val = 10
        self.assertEqual(self.TC.max_val, 10)

    def test_TextCalculator_max_str_len_get(self):
        self.assertEqual(self.TC.max_str_len, 50)

    def test_TextCalculator_max_str_len_set_fail(self):
        self.TC.max_str_len = 'a'
        self.assertEqual(self.TC.max_str_len, 50)

    def test_TextCalculator_max_str_len_set_pass(self):
        self.TC.max_str_len = 10
        self.assertEqual(self.TC.max_str_len, 10)

    def test_TextCalculator_check_excluded_pass(self):
        self.assertIsNone(self.TC_no_minus.check_excluded(node('1+2')))

    def test_TextCalculator_check_excluded_fail(self):
        self.my_regex(KeyError, "<class '_ast.Sub'>", self.TC_no_minus.check_excluded, node('1-2'))

    def test_TextCalculator_all_exclusions_present(self):
        expected = {'+', '-', '*', '/', '//', '**', '^', '%'}
        exclusion_keys = set(self.TC.exclusions.keys())
        self.assertEqual(expected, exclusion_keys)

    def test_TextCalculator_check_excluded_all_exclusions_work(self):
        operators = ['+', '-', '*', '/', '//', '**', '^', '%']
        funcs = ['Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Pow', 'BitXor', 'Mod']
        errors = ["<class '_ast.{}'>".format(func) for func in funcs]
        for index, op in enumerate(operators):
            to_test = tc.TextCalculator([op])
            self.my_regex(KeyError, errors[index], to_test.check_excluded, node('1{}1'.format(op)))

    def test_TextCalculator_check_length_pass(self):
        self.assertIsNone(self.TC.check_length('1+2'))

    def test_TextCalculator_check_length_fail(self):
        self.my_regex(SyntaxError, 'line too long: max 50', self.TC.check_length, 'a' * 51)

    def test_TextCalculator_check_length_fail_after_set(self):
        self.TC.max_str_len = 1
        self.my_regex(SyntaxError, 'line too long: max 1', self.TC.check_length, 'a' * 2)

    def test_TextCalculator_check_answer_pass(self):
        self.assertIsNone(self.TC.check_answer(1.0e+100))

    def test_TextCalculator_check_answer_fail(self):
        self.my_regex(ValueError, 'answer is larger than max value: 1e+100', self.TC.check_answer, 1.1e+100)

    def test_TextCalculator_check_answer_fail_after_set(self):
        self.TC.max_val = 1
        self.my_regex(ValueError, 'answer is larger than max value: 1', self.TC.check_answer, 2)

    def test_TextCalculator__get_nodes_pass(self):
        nodes = self.TC._get_nodes('1+2')
        self.assertEqual(nodes.left.n, 1)
        self.assertEqual(nodes.right.n, 2)
        self.assertIsInstance(nodes.op, ast.Add)

    def test_TextCalculator__get_nodes_fail(self):
        self.my_regex(SyntaxError, 'not an expression', self.TC._get_nodes, 'x = 5')

    def test_TextCalculator__node_eval_num(self):
        self.assertEqual(self.TC._node_eval(node('1')), 1)

    def test_TextCalculator__node_eval_unary_pass(self):
        self.assertEqual(self.TC._node_eval(node('+1')), 1)

    def test_TextCalculator__node_eval_unary_fail(self):
        self.my_regex(KeyError, "<class '_ast.Not'>", self.TC._node_eval, node('not 1'))

    def test_TextCalculator__node_eval_binary_pass(self):
        self.assertEqual(self.TC._node_eval(node('1+1')), 2)

    def test_TextCalculator__node_eval_binary_fail(self):
        self.my_regex(KeyError, "<class '_ast.BitAnd'>", self.TC._node_eval, node('1& 1'))

    def test_TextCalculator__node_eval_binary_fail_by_excluded(self):
        self.my_regex(KeyError, "<class '_ast.Sub'>", self.TC_no_minus._node_eval, node('1- 1'))

    def test_TextCalculator__node_eval_else_fail(self):
        self.my_regex(SyntaxError, "did not understand value or operator: <Call>",
                      self.TC._node_eval, node('int("1")'))

    def test_TextCalculator_eval_equation_pass(self):
        self.assertEqual(self.TC.eval_equation('1+2*3/(2+2)'), 2.5)

    def test_TextCalculator_eval_equation_fail(self):
        self.my_regex(SyntaxError, "<Sub> operation not allowed",
                      self.TC_no_minus.eval_equation, '1-2')

    def test_TextCalculator_safe_eval_empty(self):
        self.assertEqual(self.TC.safe_eval(''), (0, 'None'))

    def test_TextCalculator_safe_eval_pass(self):
        self.assertEqual(self.TC.safe_eval('1+2*3/(2+2)'), (2.5, 'ok'))

    def test_TextCalculator_safe_eval_fail(self):
        self.assertEqual(self.TC.safe_eval('1+2*3/0'), (0, 'division by zero'))

    def test_get_ast_class_name(self):
        self.assertEqual(tc.get_ast_class_name(str(ast.Add)), '<Add>')

    def test_get_func_name_norm(self):
        self.assertEqual(tc.get_func_name(str(ast.Add)), '<Add>')

    def test_get_func_name_special(self):
        self.assertEqual(tc.get_func_name(str(ast.BitXor)), '<Pow>')

    def test_safe_eval_empty(self):
        self.check_safe_eval('', 0, 'None')

    def test_safe_eval_excludes_fail(self):
        self.check_safe_eval('1*2+3', 0, '<Add> operation not allowed', '+', '*')

    def test_safe_eval_excludes_pass(self):
        self.check_safe_eval('1*2+3', 5, 'ok', '-', '/')

    def test_safe_eval_set_kwargs_works_max_val(self):
        self.check_safe_eval('1+2', 0, 'answer is larger than max value: 1', max_val=1)

    def test_safe_eval_set_kwargs_works_max_str_len(self):
        self.check_safe_eval('1+2', 0, 'line too long: max 1', max_str_len=1)

    def test_safe_eval_just_number(self):
        self.check_safe_eval('1', 1, 'ok')

    def test_safe_eval_add_sub_mul_div(self):
        self.check_safe_eval('1 + 2 * 3 / 4', 2.5, 'ok')

    def test_safe_eval_pow_two_kinds(self):
        self.check_safe_eval('2 ** 3 ^ 2', 64, 'ok')

    def test_safe_eval_floor_div(self):
        self.check_safe_eval('13//4', 3, 'ok')

    def test_safe_eval_mod(self):
        self.check_safe_eval('7 % 2', 1, 'ok')

    def test_safe_eval_paren(self):
        self.check_safe_eval('(1 + 2) * 2', 6, 'ok')

    def test_safe_eval_OverflowError(self):
        self.check_safe_eval('2e300 ^ 2', 0, "(34, 'Result too large')")

    def test_safe_eval_bad_syntax(self):
        self.check_safe_eval('oops I orangutan', 0, 'invalid syntax (<unknown>, line 1)')


if __name__ == '__main__':
    unittest.main()
