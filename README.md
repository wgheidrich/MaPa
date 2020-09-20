# **Ma**<font size=2>th</font>**Pa**<font size=2>rser</font>

## Introduction

MaPa is a Python library for mathematical expression parsing. It is
configurable for a large range of situations and supports the following
features:

- real-valued as well as complex-valued modes

- math functions (most of the Python math library functions are
  predefined, but program-supplied univariate and bivariate functions
  can also be defined)

- support for predefined constants as well as user defined variables
  (can be disabled)

- optional support for expressions with undefined variables
  (essentially allowing the user to define functions that can be
  evaluated by the program)

In addition to the API, MaPa also provides a stand-along command line
calculator with the same feature set.


## Contents

- [API Basics](#basics)
- [Complex Number Mode](#complex)
- [Expressions with Free Variables](#undefined)
- [Command Line Calculator](#calc)
- [Limitations and TODOs](#todo)


## API Basics<a name=basics></a>

The basic parsing operation is to create a `MaPa` object and call the
`parse` method to parse strings.

```Python
>>> from mapa.mapa import MaPa
>>> parser = MaPa()  # default settings -- variables but no complex values
>>> parser.parse('1+2*3**2')
19 
```

MaPa supports the usual Python expression syntax, with a few additions:

1. `^` can be used for powers in addition to Python's `**`
2. MaPa has a root operator `%` that works both in unary and in binary form:

```Python
>>> parser.parse('%2')
1.4142135623730951
>>> parser.parse('3%27')
3.0
```

Most of the Python `math` library functions (or `cmath` functions in
complex mode) are predefined.

```Python
>>> parser.parse('atan2(1,2)')
0.4636476090008061
```

Any missing or custom univariate or bivariate functions can be added
through the API.

If enabled, variables and variable assignments work just like in
Python. The program can also provide pre-defined constants like `pi`
or `e`:

```Python
>>> parser.parse('sin(pi/6)')
0.49999999999999994
```

MaPa can handle multi-line scripts

```Python
>>> parser.parse('''
... x = 1
... y = 2
... r = %(x^2+y^2)
... r2 = r + .1*r^2
... ''')
2.73606797749979
```

Note that the final value is the result of the last expression in the
sequence. It is also possible to use `;` as an expression separator,
so if the user can only input one line, the above example can also be
written as

```Python
>>> parser.parse('x = 1; y = 2; r = %(x^2+y^2); r+.1*r^2')
2.73606797749979
```


## Complex Number Mode <a name="complex"></a>

Complex number mode can be switched on with a parameter in the
constructor. This then allows the parsing of complex number literals
int he same syntax as Python, with a `j` suffix indicating the
imaginary unit.

```Python
>>> parser = MaPa(complex_mode=True)
>>> parser.parse('e^(pi*1j)+1')
1.2246467991473532e-16j
```

This is Euler's Identity (except for some numerical limitations of the
Python complex numbers).

The set of predefined functions in complex mode differs from that of
real valued mode, and matches the functions in the `cmath` library.

```Python
>>> parser.parse('phase(1j)-pi/2')
0.0
>>> parser.parse('abs(2j)')
2.0
>>> parser.parse('rect(1,pi/3)')
(0.5000000000000001+0.8660254037844386j)

```


## Expressions with Free Variables<a name="undefined"></a>

In a special mode, MaPa supports expressions with free
(i.e. undefined) variables. The result of such expressions is not a
value, but a partially evaluated expression tree.

```Python
>>> parser = MaPa(allow_unknown=True)
>>> expr = parser.parse('1+2*sin(x*pi/180)')
>>> expr
(1+(2*<built-in function sin>(((x*3.141592653589793)/180))))
>>> print(expr)
1+2*sin((x*3.141592653589793)/180)
>>> expr.get_undefined()
{'x': None}
```

Such an expression tree can be fully evaluated in Python by providing
the missing variable values:

```Python
>>> expr.eval({"x": 2})
1.0697989934050018
```

This allows us to essentially treat the expression tree as a function:

```
>>> [expr.eval({"x":x}) for x in range(0,360,5)]
[1.0, 1.1743114854953163, 1.3472963553338606, 1.5176380902050415, 1.6840402866513373, 1.845236523481399, 2.0, 2.147152872702092, 2.2855752193730785, 2.414213562373095, 2.532088886237956, 2.6383040885779834, 2.732050807568877, 2.8126155740733, 2.879385241571817, 2.9318516525781364, 2.9696155060244163, 2.992389396183491, 3.0, 2.992389396183491, 2.9696155060244163, 2.9318516525781364, 2.879385241571817, 2.8126155740733, 2.7320508075688776, 2.638304088577984, 2.5320888862379562, 2.414213562373095, 2.285575219373079, 2.147152872702093, 2.0, 1.845236523481399, 1.6840402866513378, 1.517638090205042, 1.3472963553338606, 1.1743114854953172, 1.0000000000000002, 0.8256885145046842, 0.6527036446661391, 0.4823619097949593, 0.3159597133486627, 0.15476347651860145, -2.220446049250313e-16, -0.14715287270209165, -0.2855752193730785, -0.4142135623730949, -0.5320888862379558, -0.6383040885779832, -0.7320508075688767, -0.8126155740732994, -0.8793852415718164, -0.9318516525781366, -0.969615506024416, -0.9923893961834911, -1.0, -0.9923893961834911, -0.9696155060244163, -0.9318516525781364, -0.8793852415718171, -0.8126155740732997, -0.7320508075688772, -0.6383040885779836, -0.5320888862379562, -0.41421356237309537, -0.28557521937307917, -0.14715287270209276, -8.881784197001252e-16, 0.1547634765186, 0.3159597133486629, 0.48236190979495863, 0.6527036446661374, 0.8256885145046834]
```

At the moment it is not possible to perform this sort of function
evaluation and variable substitution directly in the MaPa syntax.



## Command Line Calculator<a name="calc"></a>

The command line calculator is available as `mapa-calc`. It accepts
the following command line parameters:

- `--complex`: enable complex number mode
- `--no-vars`: disable processing of variables
- `--unknown`: enable parsing of expressions with undefined variables (this doesn't really have a good use at the moment other than debugging and checking the expression trees -- substitution of variables back into an expression is currently not supported from within the calculator syntax)

A simple example is shown below; the expression syntax is exactly as
described above.

```Python
sh% mapa-calc --unknown
Calculator
> 1+2
3
> a= 2*sin(x)
2*sin(x)
>
```


## Limitations and TODOs<a name="todo"></a>

There are a few limitations and TODOs

- As mentioned above, MaPa does not currently have syntax for substituting values into expressions with free variables. I might add this at some point.

- MaPa is not thread safe. This is because it uses the PLY library as a parser, which in turn relies extensively on global state. It is possible to have multiple MaPa parsers in one program (e.g. one for real valued and one for complex numbers), but they cannot be used in multiple threads in parallel.

- packaging and distribution needs some love. At the moment one can do a `pip` install, but it would be nice to have conda support and means of distribution.
