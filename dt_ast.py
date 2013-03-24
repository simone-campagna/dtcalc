#!/usr/bin/env python3

from dt import *
import sys
import ast

                
class _dt_NodeTransformer(ast.NodeTransformer):
    def __init__(self, node, *l_args, **d_args):
        self._node = node
        super(_dt_NodeTransformer, self).__init__(*l_args, **d_args)

    def visit_Name(self, node):
        if node.id == 'None':
            return ast.copy_location(self._node, node)
        else:
            return node

class DTNodeTransformer(ast.NodeTransformer):
    def __init__(self, nodes, *l_args, **d_args):
        self._nodes = nodes
        super(DTNodeTransformer, self).__init__(*l_args, **d_args)

    def visit_Str(self, node):
        if node in self._nodes:
            lineno = node.lineno
            col_offset = node.col_offset
            dt_ast = ast.parse("create_dt(None)", mode="eval")
            nt = _dt_NodeTransformer(node)
            nt.visit(dt_ast)
            for call_node in ast.walk(dt_ast):
                 if isinstance(call_node, ast.Call):
                     break
            return ast.copy_location(call_node, node)
        else:
            return node

def ast_transform(root):
    parent_node = None
    dt_class_names = set(c.__name__ for c in (Time, Duration))

    str_nodes = []
    for node in ast.walk(root):
        try:
            if isinstance(node, ast.Str):
                if isinstance(parent_node, ast.Name) and parent_node.id in dt_class_names:
                    pass
                else:
                    str_nodes.append(node)
        finally:
            parent_node = node
    nt = DTNodeTransformer(str_nodes)
    nt.visit(root)
    ast.fix_missing_locations(root)
    prev_lineno, prev_col_offset = 1, 0
    for n in ast.walk(root):
        if not hasattr(n, 'lineno'):
            n.lineno = prev_lineno
        else:
            prev_lineno = n.lineno
        if not hasattr(n, 'col_offset'):
            n.col_offset = prev_col_offset
        else:
            prev_col_offset = n.col_offset

def dt_compile(expr, filename='<input>', symbol='single', flags=0, dont_inherit=0):
    p = compile(expr, filename, symbol, flags + ast.PyCF_ONLY_AST, dont_inherit)
    ast_transform(p)
    return compile(p, filename, symbol, flags, dont_inherit)

def dt_eval(expr, symbol='single'):
    return eval(dt_compile(expr, symbol=symbol))

if __name__ == '__main__':
    import sys
    for expr in sys.argv[1:]:
        print("{0} = {1!r}".format(expr, dt_eval(expr)))

