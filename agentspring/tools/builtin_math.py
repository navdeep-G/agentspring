from . import tool
import ast, operator as op
ops={ast.Add:op.add,ast.Sub:op.sub,ast.Mult:op.mul,ast.Div:op.truediv,ast.Pow:op.pow,ast.USub:op.neg,ast.Mod:op.mod}
def _eval(node):
    if isinstance(node, ast.Num): return node.n
    if isinstance(node, ast.UnaryOp) and type(node.op) in ops: return ops[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in ops: return ops[type(node.op)](_eval(node.left), _eval(node.right))
    raise ValueError("Unsupported expression")
@tool("math_eval","Evaluate a simple arithmetic expression",parameters={"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]})
def math_eval(expr: str) -> float:
    node = ast.parse(expr, mode="eval").body
    return float(_eval(node))
