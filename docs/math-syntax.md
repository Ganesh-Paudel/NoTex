# Math syntax

NoteX translates mathematical expressions into LaTeX using a dedicated parser. It typesets expressions; it does not evaluate fractions, solve algebra, or calculate derivatives/integrals. The generated document loads [amsmath](https://ctan.org/pkg/amsmath) and `amssymb` for mathematical typesetting. No extra Python dependencies are needed.

## Inline and display math

Use `math{...}` inside a text expression for inline math:

```text
note(The probability is math{1/10}.)
formulabox(math{v=d/t})
note(bold{Remember math{x^2+y^2=z^2}.})
```

For example, the fraction generates:

```latex
\(\frac{1}{10}\)
```

Use `equation(...)` or a top-level `math{...}` for an unnumbered display equation:

```text
equation((x+1)/(x-1))
math{sqrt(x^2+y^2)}
```

Ordinary text remains escaped plain text. Write `math\{1/10\}` in a note to show the syntax literally. Raw `$...$`, `\frac`, Python expressions, and other backslash commands are not accepted as math input.

## Algebra and grouping

| Input | Meaning |
| --- | --- |
| `a+b`, `a-b`, `-x`, `+x` | Addition, subtraction, and unary signs. |
| `a*b` | Multiplication, rendered with a centered dot. |
| `a/b` | A fraction, rendered as `\frac{a}{b}`. |
| `(a+b)/(c-d)` | A fraction with compound numerator and denominator. |
| `x^2` or `x**2` | A power. |
| `x_i`, `x_{i+1}`, `x_i^2` | Subscripts, grouped subscripts, and combined scripts. |
| `x^2^3` | Right-associative power: `x^(2^3)`. |
| `-x^2`, `(-x)^2` | Different expressions; explicit grouping preserves the distinction. |
| `2x`, `2(x+1)`, `(x+1)y` | Implicit multiplication. |
| `f(x)`, `density(x)` | A named function call. Use `x*(y+1)` for multiplication by a grouped expression. |
| `n!`, `x_i!` | Factorial notation. |
| `1.5e-3` | Scientific notation: `1.5` times `10` to the power `-3`. |

Multiplication and division have the same precedence and associate left: `a/b/c` means `(a/b)/c`, and `a/b*c` means `(a/b)*c`. Use `a/(b*c)` when the whole product belongs in the denominator. Power binds more tightly than unary signs, then multiplication/division, then addition/subtraction, then relations. Use braces or parentheses around complex script contents: `x^{n+1}`. `x^2_i` and `x_i^2` both give a subscripted and squared variable. Group a scripted base before adding another exponent, for example `(x^2)^3`.

Relations: `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `~=`, and `->`. `+-` or `+/-` gives plus-or-minus, including as a unary sign. Unicode `±`, `×`, `·`, `÷`, `−`, `≤`, `≥`, `≠`, `≈`, and `→` are also recognized. For example, `x=(-b+/-sqrt(b^2-4*a*c))/(2*a)` typesets the quadratic formula.

## Nested functions

Arguments are comma-separated mathematical expressions. Except where noted, the expression comes first, then a variable/index, then bounds.

| Syntax | Example |
| --- | --- |
| `sqrt(expression)` | `sqrt(1/10)` |
| `root(expression,index)` | `root(x,3)` for a cube root. |
| `frac(numerator,denominator)` | `frac(x+1,x-1)`; equivalent to `(x+1)/(x-1)`. |
| `summation(expression,index,lower,upper)` | `summation(i^2,i,1,n)` |
| `product(expression,index,lower,upper)` | `product(i,i,1,n)` |
| `integral(expression,variable)` | `integral(x^2,x)` |
| `integral(expression,variable,lower,upper)` | `integral(x^2,x,0,1)` |
| `derivative(expression,variable)` | `derivative(x^3,x)` |
| `derivative(expression,variable,order)` | `derivative(x^3,x,2)` |
| `partial(expression,variable[,order])` | `partial(x^2*y,x,2)` |
| `limit(expression,variable,value)` | `limit(sin(x)/x,x,0)` |
| `abs(expression)` | `abs(x-1)` |
| `binom(n,k)` | `binom(n,k)` |
| `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `ln`, `exp` | `sin(pi*x)`; each takes one argument. |
| `log(expression[,base])` | `log(x)` or `log(x,2)` |

Aliases: `sum` for `summation`, `prod` for `product`, `int`/`integrals` for `integral`, and `diff`/`derivatives` for `derivative`. Built-in function names are case-insensitive. Other ASCII names such as `f(x)` or `density(x)` typeset ordinary functions; they are not executed. Derivative orders must be positive integer literals. Variables/indices must be identifiers or subscripted identifiers such as `x_i`.

Examples with children nested inside other functions:

```text
equation(sqrt(summation(i^2,i,1,n)))
equation(integral(sqrt(1+x^2),x,0,1))
equation(integral(integral(x*y,x,0,1),y,0,2))
equation(partial(partial(f(x,y),x),y))
equation(limit((f(x+h)-f(x))/h,h,0))
equation(P(X=k)=binom(n,k)*p^k*(1-p)^{n-k})
```

## Greek letters and constants

Common Greek names such as `alpha`, `beta`, `gamma`, `theta`, `lambda`, `mu`, `pi`, `sigma`, `phi`, and `omega` become Greek symbols. Uppercase names such as `Gamma`, `Delta`, `Theta`, `Lambda`, `Pi`, `Sigma`, `Phi`, `Psi`, and `Omega` are supported where LaTeX has distinct symbols. Standard Unicode Greek characters are also recognized. For example, `alpha+pi` and `α+π` render alike.

`inf`, `infinity`, `oo`, and `∞` render infinity. `hbar` and `nabla` are also available. Other identifiers contain ASCII letters and digits; `_` introduces a subscript rather than being part of an identifier.

## New lines

Inside math, top-level source newlines, semicolons, and `newline()` split rows:

```text
equation(
  a=(x+1)^2
  =x^2+2*x+1
  b=a/2
)
note(Two equations: math{x=1; y=2}.)
math{x=1 newline() y=2}
```

Multiple rows use LaTeX's `aligned` environment. Equation rows align at the outermost relation; rows without a relation align at their start. Later rows may start with a relation such as `=` to omit the previous left-hand side. Leading/trailing blank math lines and repeated row separators are ignored.

Newlines within parentheses, brackets, braces, or function arguments are whitespace, so a long function call can wrap in the source without adding a rendered row. Explicit `;` or `newline()` separators inside those groups are rejected; put them between complete equations.

For text paragraphs and boxes, use an explicit `newline()`:

```text
note(First line. newline() Second line.)
newline()
note(A new paragraph after extra spacing.)
```

Ordinary text source newlines continue to behave as spaces, and blank text lines continue to separate paragraphs. To print the literal name and parentheses, use `newline\(\)`.

## Diagnostics and limits

Math nodes and their child expressions retain spans into the original notes source. Invalid characters, missing/mismatched delimiters, wrong function argument counts, invalid calculus variables/orders, and duplicate scripts report a `ParseError` with the original line and column. The CLI's `--json` output retains the same diagnostic fields as text syntax errors. A malformed equation cannot overwrite the previous successful output.

Math structural depth is bounded to the same 64-level budget as text formatting, including enclosing text styles, grouping, and expression-tree height. Very long operator chains count toward tree depth; break complex expressions into simpler expressions or multiple rows rather than building an arbitrarily deep tree. The grammar covers mathematical typesetting, not a full computer algebra system; matrices, equation labels, symbolic computation, and raw LaTeX extensions are not implemented.
