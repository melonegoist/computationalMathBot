import math
import numpy as np
from .tools import parse_equations


def bisection_method(equation: str, a: float, b: float, accuracy: float, bisection_counter : int = 0) -> tuple[float, float, int]:
    """
    Finds a root of a given equation within a specified interval using the Bisection Method.

    The function recursively narrows down the interval [a, b] until the desired accuracy is achieved.
    It evaluates the equation at the midpoint and checks the sign change to determine the subinterval containing the root.

    Args:
        equation (str): A mathematical equation in terms of 'x' (e.g., "x**2 - 2").
        a (float): The left endpoint of the initial interval.
        b (float): The right endpoint of the initial interval.
        accuracy (float): The desired accuracy (tolerance) for the root approximation.
        bisection_counter (int, optional): Counter for the number of bisections performed. Defaults to 0.

    Returns:
        tuple[float, float, int]: A tuple containing:
            - The approximate root (x).
            - The value of the equation at the root (f(x)).
            - The total number of bisections performed.

    Raises:
        ValueError: If the initial interval [a, b] does not satisfy f(a) * f(b) < 0 (no root in the interval).

    Example:
        >>> bisection_method("x**2 - 2", 1.0, 2.0, 0.001)
        (1.4140625, -0.00042724609375, 10)
    """

    while math.fabs(b - a) > accuracy:
        mid = (a + b) / 2
        
        if eval(equation, {"x": mid}) * eval(equation, {"x": a}) > 0:
            bisection_counter += 1
            return bisection_method(equation, mid, b, accuracy, bisection_counter)
        else:
            bisection_counter += 1
            return bisection_method(equation, a, mid, accuracy, bisection_counter)
        

    x = (a + b) / 2

    return (x, eval(equation, {"x": x}), bisection_counter)


def secant_method(func, x0, x1, accuracy, max_iter=100):
    try:
        allowed_names = {'x': None, 'math': math}
        code = compile(func, "<string>", "eval")

        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(f"Использование '{name}' запрещено")
        
        f = lambda x: eval(func, {'__builtins__': None}, {'x': x, 'math': math})

    except Exception as e:
        print(f"Ошибка в функции: {e}")
        return None, None, 0

    for iteration in range(1, max_iter + 1):
        try:
            f_x0 = f(x0)
            f_x1 = f(x1)
        except:
            print("Ошибка при вычислении функции на {iteration} итерации")
            return None, None, iteration

        if abs(f_x1) < accuracy:
            return x1, f_x1, iteration

        try:
            denominator = f_x1 - f_x0
            if abs(denominator) < 1e-15:
                return None, None, iteration
            
            x_next = x1 - f_x1 * (x1 - x0) / denominator

        except ZeroDivisionError:
            return None, None, iteration

        x0, x1 = x1, x_next

        if abs(x1 - x0) < accuracy:
            return x1, f(x1), iteration

    return None, None, max_iter


def simple_iteration_method(func: str, a: float, b: float, accuracy: float, max_iter: int=100):
    """
    ## Solves x = φ(x) using simple iterations.

    ### Parameters:
    - func - string with function φ(x) of the form: "math.cos(x)"
    - a, b - interval boundaries
    - accuracy - accuracy
    - max_iter - maximum number of iterations (default 100)

    ### Returns a tuple of values:
    - found root of the equation: x
    - found value of the function at the root: f(x)
    - number of iterations performed
    """

    try:
        allowed_names = {'x': None, 'math': math}
        code = compile(func, "<string>", "eval")

        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(f"Запрещённое имя: '{name}'")
        
        phi = lambda x: eval(func, {'__builtins__': None}, {'x': x, 'math': math})

    except Exception as e:
        print(f"Ошибка в функции: {e}")

        return None, None, 0

    try:
        phi_a, phi_b = phi(a), phi(b)
    except:
        print("Ошибка при вычислении φ(a) или φ(b)")
        return None, None, 0

    if not (a <= phi_a <= b) or not (a <= phi_b <= b):
        print("φ не отображает [a, b] в себя! Метод может не сойтись.")

    x_prev = (a + b) / 2

    for iteration in range(1, max_iter + 1):
        try:
            x_next = phi(x_prev)
        except:
            print("Ошибка вычисления φ(x)")
            return None, None, iteration

        if x_next < a or x_next > b:
            print(f"x вышло за границы [{a}, {b}]")
            return None, None, iteration

        if abs(x_next - x_prev) < accuracy:
            return x_next, phi(x_next), iteration

        x_prev = x_next

    print(f"Не сошлось за {max_iter} итераций.")

    return None, None, max_iter


def newton_method(equation: str, x0: float, y0: float, tol: float, max_iter: int=100, h: float=1e-6) -> tuple[float, float, float, float, int]:
    """
    ### Solves a system of equations using Newton's method.

    #### Parameters:
    - equation: string like "x**2 + y = 4; y = sin(x)"
    - x0, y0: initial guesses
    - tol: precision
    - max_iter: maximum number of iterations (default 100)
    - h: step for numerical Jacobian (default 1e-6)

    #### Returns a tuple of values:
    - root of system x
    - root of system y
    - value of first function in (x, y)
    - value of second function in (x, y)
    - number of iterations
    """

    try:
        F = parse_equations(equation)
        
    except ValueError as e:
        print(f"Ошибка парсинга уравнений: {e}")
        return None, None, None, None, 0
    
    x, y = x0, y0
    for iteration in range(1, max_iter + 1):
        F_val = np.array(F(x, y))
        
        J = np.zeros((2, 2))
        
        # df1/dx, df1/dy
        f1_x_plus_h = F(x + h, y)[0]
        f1_y_plus_h = F(x, y + h)[0]
        J[0, 0] = (f1_x_plus_h - F_val[0]) / h
        J[0, 1] = (f1_y_plus_h - F_val[0]) / h
        
        # df2/dx, df2/dy
        f2_x_plus_h = F(x + h, y)[1]
        f2_y_plus_h = F(x, y + h)[1]
        J[1, 0] = (f2_x_plus_h - F_val[1]) / h
        J[1, 1] = (f2_y_plus_h - F_val[1]) / h
        
        try:
            dx, dy = np.linalg.solve(J, -F_val)

        except np.linalg.LinAlgError:
            print("Матрица Якоби вырождена!")
            return None, None, None, None, iteration
        
        x += dx
        y += dy
        
        if np.sqrt(dx**2 + dy**2) < tol:
            f1, f2 = F(x, y)
            return x, y, f1, f2, iteration
    
    print(f"Не сошлось за {max_iter} итераций.")
    f1, f2 = F(x, y)

    return x, y, f1, f2, max_iter

