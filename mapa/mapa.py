
import math as m
import cmath as cm

import ply.lex as lex
import ply.yacc as yacc

import expression as exp


class MaPa:
    '''
    Math Parser
    
    a class for parsing math expressions that supports

    - real and complex numbers
    - function calls and variable definitions
    - fully and partially defined expressions
      (i.e those that can be reduced to a value and those with undefined
       variables that return an expression tree)
    '''

    # default univariate functions for real value mode
    def_real_univar = {
        "exp":      m.exp,
        "expm1":    m.expm1,
        "log":      m.log,
        "log1p":    m.log1p,
        "log2":     m.log2,
        "log10":    m.log10,
        "sqrt":     m.sqrt,
        "asin":     m.asin,
        "acos":     m.acos,
        "atan":     m.atan,
        "cos":      m.cos,
        "sin":      m.sin,
        "tan":      m.tan,
        "fabs":     m.fabs,
        "floor":    m.floor,
        "ceil":     m.ceil,
    }

    # default biivariate functions for real value mode
    def_real_bivar = {
        "pow":      m.pow,
        "atan2":    m.atan2,
        "log":      m.log,
    }
    
    
    # default univariate functions for complex value mode
    def_complex_univar ={
        "phase":    cm.phase,
        "polar":    cm.polar,
        "rect":     cm.rect,
        "exp":      cm.exp,
        "log":      cm.log,
        "log10":    cm.log10,
        "sqrt":     cm.sqrt,
        "asin":     cm.asin,
        "acos":     cm.acos,
        "atan":     cm.atan,
        "cos":      cm.cos,
        "sin":      cm.sin,
        "tan":      cm.tan,
    }

    
    # default bivariate functions for complex value mode
    def_complex_bivar = {
        "log":      cm.log,
    }
    
    # default constant set
    constants = {
        "pi":       m.pi,
        "e":        m.e,
    }


    def __init__(self,
                 complex_mode = False,
                 allow_vars = True,
                 allow_unknown = True,
                 variables = {},
                 consts = None,
                 bivar = None,
                 univar = None ):
        '''
        Initialization

        Parameters:
            - complex_mode :    whether to use real or complex numbers
                                (default: False)

            - allow_vars :      whether allow userpdefined variables
                                (default: True)

            - allow_unknown :   allow expressions with unknown variables that
                                are returned as Expression objects

            - variables :       initial dictionary of variables (default: empty)

            - consts :          initial dictionary of constants
                                (default: None, which means deafult constants)

            - bivar :           list of bivariate functions
                                (default: pi and e)
        
            - univar :          list of univariate functions (default: None)
                                if None, the deault set will be chosen
                                according to complex_mode
        '''
        self.is_complex = complex_mode
        self.use_vars   = allow_vars
        self.allow_unknown   = allow_unknown
        self.variables  = variables
        self.constants  = consts if consts != None else MaPa.constants
        if complex_mode:
            self.bivar = bivar if bivar != None else MaPa.def_complex_bivar
            self.univar = univar if univar != None else MaPa.def_complex_univar
        else:
            self.bivar = bivar if bivar != None else MaPa.def_real_bivar
            self.univar = univar if univar != None else MaPa.def_real_univar

            
    def parse(self,str):
        '''
        parse a math expression from a string
        
        Parameters:
            - str :     the math expression string

        Returns:
            EITHER a value (int, float, complex number) if only known
                variables are used in the expression
            OR an Expression object representing a partially evaluated
                expression
        '''
        global mapars
        mapars = self
        result = mapa_parser.parse(str)
        mapars = None
        return result



###################################################################
# This is the current MaPa instance usde for parsing
# 
# (unfortunately global state due to the way PLY works)
###################################################################

mapars = None



#######
# lexer
#######


# tokens
tokens = (
    'NEWLINE',
    'ASSIGN',
    'LPAR',
    'RPAR',
    'COMMA',
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'EXP',
    'ROOT',
    'INT',
    'NUMBER',
    'IDENTIFIER',
)



# single character tokens
t_ASSIGN = r'='
t_LPAR =   r'\('
t_RPAR =   r'\)'
t_COMMA =  r','
t_ADD =    r'\+'
t_SUB =    r'-'
#t_MUL =    r'\*'
t_DIV =    r'/'
t_EXP =    r'\^'
t_ROOT =   r'%'


# this can be either MUL or EXP in Python syntax depending on the number of *s
def t_MUL(t):
    r'\*\*?'
    if len(t.value) > 1:
        t.type = "EXP"
        t.value = '^'
    return t

# variable/constant names and builtin functions
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

## !!!! do complex number version
def t_NUMBER(t):
    r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?j?'
    if t.value[-1] == 'j':
        if mapars.is_complex:
            t.value = complex(t.value)
        else:
            raise(NotImplementedError("Complex numbers not supported"))
    else:
        t.value = float(t.value)
        if t.value.is_integer():
            t.type = "INT"
            t.value = int(t.value)
    return t


#def t_comment(t):
#    r'\#[^\n]*'
#    pass

# Define a rule so we can track line numbers
def t_NEWLINE(t):
    r'[;\n]+'
    t.lexer.lineno += len(t.value)
    return t
    
# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    raise(SyntaxError("Illegal character:\n  \"... "+t.value[0:10]+"...\"\n       ^"))
    

# Build the lexer
mapa_lexer = lex.lex(optimize=1,lextab='mapa_lextab')





##########
# parser
##########


precedence = (
    ('left','ADD','SUB'),
    ('left','MUL','DIV'),
    ('right','UMINUS'),
    ('left','EXP','ROOT'),
    ('right','UROOT')
)

def p_lineseq(t):
    '''
    lines : lines NEWLINE line
          | line
    '''
    if len(t) == 4 and t[3] != None:
        t[0] = t[3]
    else:
        t[0] = t[1]


def p_oneline(t):
    '''
    line : statement
         | empty
    '''
    t[0] = t[1]


def p_empty(t):
    'empty :'
    pass


def p_statement_assign(t):
    '''
    statement : IDENTIFIER ASSIGN expr
              | expr
    '''
    if len(t) == 4 and not mapars.use_vars:
        raise(NotImplementedError("Assignment not supported"))
    else:
        if len(t) == 4:
            t[0] = t[3]
            mapars.variables[t[1]] = t[3]
        else:
            t[0] = t[1]
            mapars.variables[t[1]] = t[1]
            

    
def p_expr_binop(t):
    '''
    expr : expr ADD expr
    expr : expr SUB expr
    expr : expr MUL expr
    expr : expr DIV expr
    expr : expr EXP expr
    expr : expr ROOT expr
    '''
    if isinstance(t[1],exp.Expression) or isinstance(t[3],exp.Expression):
        # dealing with partially defined expression -- create expression tree
        t[0] = exp.BinOpExpr(t[2],t[1],t[3])
    else:
        # otherwise, evaluate directly
        if t[2] == '+'  :
            t[0] = t[1] + t[3]
        elif t[2] == '-':
            t[0] = t[1] - t[3]
        elif t[2] == '*':
            t[0] = t[1] * t[3]
        elif t[2] == '/':
            t[0] = t[1] / t[3]
        elif t[2] == '^':
            t[0] = t[1] ** t[3]
        elif t[2] == '%':
            t[0] = t[3] ** (1/t[1])


def p_expr_uminus(t):
    'expr : SUB expr %prec UMINUS'
    if isinstance(t[2],exp.Expression):
        t[0] = exp.UniOpExpr(t[1],t[2])
    else:
        t[0] = -t[2]

        
def p_expr_uroot(t):
    'expr : ROOT expr %prec UROOT'
    if isinstance(t[2],exp.Expression):
        t[0] = exp.UniOpExpr(t[1],t[2])
    else:
        t[0] = t[2] ** 0.5

        
def p_expr_univar(t):
    'expr : IDENTIFIER LPAR expr RPAR'
    try:
        func = mapars.univar[t[1]]
    except KeyError:
        raise(NameError("Unknown univariate function "+t[1]))
    if isinstance(t[3],exp.Expression):
        t[0] = exp.UniFuncExpr(t[1],func,t[3])
    else:
        t[0] = func(t[3])

    
def p_expr_bivar(t):
    'expr : IDENTIFIER LPAR expr COMMA expr RPAR'
    try:
        func = mapars.bivar[t[1]]
    except KeyError:
        raise(NameError("Unknown biivariate function "+t[1]))
    if isinstance(t[3],exp.Expression) or isinstance(t[5],exp.Expression):
        t[0] = exp.UniFuncExpr(t[1],func,t[3],t[5])
    else:
        t[0] = func(t[3],t[5])


def p_expr_group(t):
    'expr : LPAR expr RPAR'
    t[0] = t[2]


def p_expr_const(t):
    '''
    expr : INT
    expr : NUMBER
    '''
    t[0] = t[1]


def p_expr_var(t):
    'expr : IDENTIFIER'
    t[0] = mapars.variables.get(t[1],None)
    if t[0] == None:
        t[0] = mapars.constants.get(t[1],None)

    if t[0] == None:
        if mapars.allow_unknown:
            t[0] = exp.VarExpr(t[1])
        else:
            raise(NameError('Unknown variable or constant '+t[1]))

    
def p_error(t):
    raise(SyntaxError("Syntax error at '%s'" % t.value))


mapa_parser = yacc.yacc(optimize=1,tabmodule='mapa_parsetab')


def main():
    import readline
    import sys
    import argparse

    ap = argparse.ArgumentParser(description='Commandline calculator.')
    ap.add_argument('--unknown', dest='allow_unknown',
                    action='store_const', const=True, default=False,
                    help='allow expressions with unknown variables')
    ap.add_argument('--complex', dest='complex_mode',
                    action='store_const', const=True, default=False,
                    help='switch on complex number mode')
    ap.add_argument('--no-vars', dest='allow_vars',
                    action='store_const', const=False, default=True,
                    help='switch off use of variables')
    args = ap.parse_args()
    
    myparser = MaPa(complex_mode = args.complex_mode,
                    allow_vars = args.allow_vars,
                    allow_unknown = args.allow_unknown)
    
    print('Calculator')
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        try:
            result = myparser.parse(s)
            if result != None:
                print(result)
        except Exception as e:
            print("Error:",e,file=sys.stderr)
    
    print("\nGoodbye...")


if __name__ == '__main__':
    main()

