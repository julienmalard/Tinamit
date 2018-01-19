?ec: sum
      | var "=" sum    -> assign_var
?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: NUM           -> number
     | "-" atom         -> neg
     | var
     | "(" sum ")"
     | func

func: NOMBRE "(" args ")"

args: sum ("," sum)*

PRB : "PRB"
varbase: NOMBRE | CADENA
var: varbase
    | varbase "[" varbase+ ("," varbase)* "]" -> subs


CADENA: /(".+"(?<!\\))/
NOMBRE : /[a-zA-Z]+[a-zA-Z0-9 ]*/

NUM : NUMBER
    | ["-"] NUMBER

%import common.NUMBER

%import common.WS
%ignore WS