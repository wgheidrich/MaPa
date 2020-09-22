# math expression tree classes
# Author: Wolfgang Heidrich

class Expression:
    '''
    Base class for math expressions -- needs to be subclassed
    '''

    def __init__(self):
        'initialization'
        pass

    
    def eval(self,vars):
        '''
        Evaluate parse tree
        
        Must be implemented by subclasses
        
        Parameters:
            vars :      dictionary of variables and their values

        Returns:
            EITHER a value (int, float,..) if all variables used in the
                   expression are provided
            OR     a new (simplified) parse tree with the provided variables
                   subsituted for their values, and then simplified
        '''
        raise(NotImplemented)

    def get_undefined(self):
        '''
        return dict of undefined variables by recursively traversing the tree
        
        Returns:
            dict of variable names (with value None)
        '''
        raise(NotImplemented)
    
    def format(self,priority,readable=True):
        '''
        format the expression as a string

        must be implemented by subclasses
        
        Parameters:
            priority : priority level of the parent operator (determines the
                       use of brackets
        
            readable : produce readable string vs. internal representation

        Returns:
            string representation
        '''
        raise(NotImplemented)
        
    def __str__(self):
        '''
        string conversion
        '''
        return self.format(0)

    def __repr__(self):
        '''
        representation
        
        same as string but always fully bracketed
        '''
        return self.format(0,False)



class VarExpr(Expression):
    '''
    Expression node for a variable
    '''

    def __init__(self,name):
        '''
        Initialization
        
        Parameters:
            name :      the name of the variable
        '''
        self.name = name

    
    def eval(self,vars):
        '''
        Evaluate variable
        
        If the the name of this variable is in th eprovided variable list,
        it is substituted for its value and returned. Otherwise, self is
        returned unaltered.
       
        Parameters:
            vars :      dictionary of variables and their values

        Returns:
            EITHER value or SELF
        '''
        return vars.get(self.name,self)

    
    def get_undefined(self):
        '''
        return dict of undefined variables by recursively traversing the tree
        
        Returns:
            dict of variable names
        '''
        return {self.name : None}

    
    def format(self,priority,readable=True):
        '''
        format the expression as a string

        Parameters:
            priority : ignored for VarExpr

            readable : produce readable string vs. internal representation
                       (ignored for VarExpr)

        Returns:
            variable name as string
        '''
        return self.name

    
class UniOpExpr(Expression):
    '''
    Unary Operator Expression
    
    one of the operators - or %
    (where % denotes the square root, as in %a is the square root of a)
    '''
    
    op_priorities = {
        '-' : 3,
        '%' : 7
    }

    def __init__(self,op,operand):
        '''
        Initialization
        
        Parameters:
            op :        string of the operator symbol (see list above)
        
            operand :   operand (node of class Expression or value)
        '''
        if op in UniOpExpr.op_priorities.keys():
            self.op = op
        else:
            raise NotImplementedError("Unknown operator "+op)
        self.operand = operand

        
    def eval(self,vars):
        '''
        evaluate unary operator
        
        recursively evaluate the operand and apply operator

        Parameters:
            vars :     dictionary of variables and their values

        Returns:
            either a value, or new Expression if the operand is not
            fully defined
        '''
        operand = self.operand.eval(vars)\
            if isinstance(self.operand,Expression) else self.operand
        
        if isinstance(operand,Expression):
            return UniOpExpr(self.op,operand)
        elif self.op == '-':
            return - operand
        elif self.op == '%':
            return operand ** 0.5
        # we shouldn't really get here, since this is checked in __init__
        raise NotImplementedError("Unknown operator "+op)


    def get_undefined(self):
        '''
        return dict of undefined variables by recursively traversing the tree
        
        Returns:
            dict of variable names
        '''
        if isinstance(self.operand,Expression):
            return self.operand.get_undefined()
        else:
            return {}

        
    def format(self,priority,readable=True):
        '''
        format the expression as a string

        Parameters:
            priority :  operator priority of the parent
                        the output will be bracketed if this is lower than the
                        priority of self or if readable is False

            readable :  produce readable string vs. internal representation

        Returns:
            variable name as string 
        '''
        if isinstance(self.operand,Expression):
            estr = self.operand.format(UniOpExpr.op_priorities[self.op],
                                       readable)
        else:
            estr = str(self.operand)
        return '('+self.op+estr+')' if not readable or\
            priority > UniOpExpr.op_priorities[self.op] else self.op+estr

        
class BinOpExpr(Expression):
    '''
    Binary Operator Expression
    
    one of the operators +,-,*,/,^, or %
    (where % denotes the root, as in 3%a is the cube root of a)
    '''

    op_priorities = {
        '+' : 0,
        '-' : 1,  # higher than + so that a-(b+c) gets bracketed the right way
        '*' : 3,
        '/' : 4,  # same reason as -
        '^' : 5,
        '%' : 6
    }
    
    def __init__(self,op,operand1,operand2):
        '''
        Initialization
        
        Parameters:
            op :        string of the operator name (one of the ones listed 

            operand1 :  first operand (node of class Expression or value)

            operand2 :  second operand (node of class Expression or value)
        '''
        if op in BinOpExpr.op_priorities.keys():
            self.op = op
        else:
            raise NotImplementedError("Unknown operator "+op)
        self.operands = (operand1,operand2)


    def eval(self,vars):
        '''
        evaluate binary operator
        
        recursively evaluate the operands and apply operator

        Parameters:
            vars :      dictionary of variables and their values
        
        Returns:
            either a value, or new Expression if the operands are not
            fully defined
        '''
        operand1 = self.operands[0].eval(vars)\
            if isinstance(self.operands[0],Expression) else self.operands[0]
        operand2 = self.operands[1].eval(vars)\
            if isinstance(self.operands[1],Expression) else self.operands[1]
        
        if isinstance(operand1,Expression) or isinstance(operand2,Expression):
            return BinOpExpr(self.op,operand1,operand2)
        elif self.op == '+':
            return operand1 + operand2
        elif self.op == '-':
            return operand1 - operand2
        elif self.op == '*':
            return operand1 * operand2
        elif self.op == '/':
            return operand1 / operand2
        elif self.op == '^':
            return operand1 ** operand2
        elif self.op == '%':
            return operand2 ** (1/operand1)
        # we shouldn't really get here, since this is checked in __init__
        raise NotImplementedError("Unknown operator "+op)

    
    def get_undefined(self):
        '''
        return dict of undefined variables by recursively traversing the tree
        
        Returns:
            dict of variable names
        '''
        v1 = self.operands[0].get_undefined()\
            if isinstance(self.operands[0],Expression) else {}
        v2 = self.operands[1].get_undefined()\
            if isinstance(self.operands[1],Expression) else {}
        v1.update(v2)
        return v1


    def format(self,priority,readable=True):
        '''
        format the expression as a string

        Parameters:
            priority :  operator priority of the parent
                        the output will be bracketed if this is lower than the
                        priority of self

            readable :  produce readable string vs. internal representation

        Returns:
            variable name as string 
        '''
        if isinstance(self.operands[0],Expression):
            estr = self.operands[0].format(BinOpExpr.op_priorities[self.op],
                                           readable)
        else:
            estr = str(self.operands[0])
        estr += self.op
        if isinstance(self.operands[1],Expression):
            estr += self.operands[1].format(BinOpExpr.op_priorities[self.op],
                                            readable)
        else:
            estr += str(self.operands[1])
        return '('+estr+')' if not readable or\
            priority > BinOpExpr.op_priorities[self.op] else estr


class UniFuncExpr(Expression):
    '''
    Uivariate Function Expression
    '''
    
    def __init__(self,name,func,operand):
        '''
        Initialization
        
        Parameters:
            name :      name of the function for string representations

            func :      the python function to call

            operand :   operand (node of class Expression or value)
        '''
        self.name = name
        self.func = func
        self.operand = operand

        
    def eval(self,vars):
        '''
        evaluate unary operator
        
        recursively evaluate the operand and apply operator

        Parameters:
            vars :      dictionary of variables and their values
        
        Returns:
            either a value, or self if the operand is not fully defined
        '''
        operand = self.operand.eval(vars)\
            if isinstance(self.operand,Expression) else self.operand

        if isinstance(operand,Expression):
            return UniFuncExpr(self.name,self.func,operand)
        else:
            return self.func(operand)


    def get_undefined(self):
        '''
        return dict of undefined variables by recursively traversing the tree
        
        Returns:
            dict of variable names
        '''
        if isinstance(self.operand,Expression):
            return self.operand.get_undefined()
        else:
            return {}


    def format(self,priority,readable=True):
        '''
        format the expression as a string

        Parameters:
            priority :  ignored for UniFuncExpr

            readable :  produce readable string vs. internal representation

        Returns:
            string with function call syntax
        '''
        if isinstance(self.operand,Expression):
            estr = self.operand.format(0,readable)
        else:
            estr = str(self.operand)
        return (self.name if readable else str(self.func))+'('+estr+')'


        
class BinFuncExpr(Expression):
    '''
    Bivariate Function Expression
    '''
    def __init__(self,name,func,operand1,operand2):
        '''
        Initialization
        
        Parameters:
            name :      name of the function for string representations

            func :      the python function to call

            operand1 :  first operand (node of class Expression or value)

            operand2 :  second operand (node of class Expression or value)
        '''
        self.name = name
        self.func = func,
        self.operands = (operand1,operand2)


    def eval(self,vars):
        '''
        evaluate binary operator
        
        recursively evaluate the operands and apply operator

        Parameters:
            vars :      dictionary of variables and their values
        
        Returns:
            either a value, or self if the operand is not fully defined
        '''
        operand1 = self.operands[0].eval(vars)\
            if isinstance(self.operands[0],Expression) else self.operands[0]
        operand2 = self.operands[1].eval(vars)\
            if isinstance(self.operands[1],Expression) else self.operands[1]
        
        if isinstance(operand1,Expression) or isinstance(operand2,Expression):
            return BinFuncExpr(self.name,self.func,operand1,operand2)
        else:
            return func(operand1,operand2)

    
    def get_undefined(self):
        '''
        return dict of undefined variables by recursively traversing the tree
        
        Returns:
            dict of variable names
        '''
        v1 = self.operands[0].get_undefined()\
            if isinstance(self.operands[0],Expression) else {}
        v2 = self.operands[1].get_undefined()\
            if isinstance(self.operands[1],Expression) else {}
        v1.update(v2)
        return v1


    def format(self,priority,readable=True):
        '''
        format the expression as a string

        Parameters:
            priority :  ignored for BinFuncExpr

            readable :  produce readable string vs. internal representation

        Returns:
            string with function call syntax
        '''
        if isinstance(self.operands[0],Expression):
            estr1 = self.operands[0].format(0,readable)
        else:
            estr1 = str(self.operands[0])
        if isinstance(self.operands[1],Expression):
            estr2 += self.operands[1].format(0,readable)
        else:
            estr2 += str(self.operands[1])
        return (self.name if readable else str(self.func))+'('+estr1+','+estr2+')'


def __test__():
    import math as m
    
    expr = BinOpExpr('+',
                     BinOpExpr('-',
                               1,
                               UniFuncExpr("cos",
                                           m.cos,
                                           BinOpExpr('/',m.pi,3)
                               )
                     ),
                     BinOpExpr('*',
                               VarExpr("x"),
                               VarExpr("y")
                               )
    )

    title = "Expression Tree Example"
    print('\n'+title+'\n'+'='*len(title)+'\n')
    print("Undefined vars:\t", expr.get_undefined())
    print("Internal repr.:\t", expr.__repr__())
    print("Readable repr:\t",expr)
    eval = expr.eval({})
    print("Simplified:\t",eval)
    evalx = eval.eval({"x":1})
    print("x = 1:\t\t",evalx)
    evaly = eval.eval({"x":1,"y":2})
    print("x = 1, y = 2:\t",evaly)
    print()
    


if __name__ == '__main__':
    __test__()
