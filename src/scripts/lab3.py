import math

def evaluate_function(func_str, x):
    """Calculates the value of the function func_str at point x"""
    try:
        # Replace '^' with '**' to support exponent notation
        func_str = func_str.replace('^', '**')
        # Calculate the value of the function at point x
        return eval(func_str, {'x': x, 'math': math, 'sin': math.sin, 'cos': math.cos, 
                              'exp': math.exp, 'sqrt': math.sqrt, 'log': math.log})
    except Exception as e:
        raise ValueError(f"Error evaluating function: {e}")


def runge_rule(I_h, I_h2, k, eps):
    """Accuracy check using Runge's rule"""
    return abs(I_h - I_h2) / (2**k - 1) < eps


def rectangle_left(func_str, a, b, n):
    """Left rectangle method"""
    h = (b - a) / n
    return h * sum(evaluate_function(func_str, a + i * h) for i in range(n))


def rectangle_right(func_str, a, b, n):
    """Right Rectangle Method"""
    h = (b - a) / n
    return h * sum(evaluate_function(func_str, a + (i + 1) * h) for i in range(n))


def rectangle_mid(func_str, a, b, n):
    """Mean Rectangle Method"""
    h = (b - a) / n
    return h * sum(evaluate_function(func_str, a + (i + 0.5) * h) for i in range(n))


def trapezoidal(func_str, a, b, n):
    """Trapezoid Method"""
    h = (float(b) - float(a)) / n
    return h * (0.5 * (evaluate_function(func_str, a) + evaluate_function(func_str, b)) + 
                sum(evaluate_function(func_str, a + i * h) for i in range(1, n)))


def simpson(func_str, a, b, n):
    """Simpson's Method"""
    if n % 2 != 0:
        n += 1  # make sure that n is even
    h = (b - a) / n
    sum_odd = sum(evaluate_function(func_str, a + (2 * i - 1) * h) for i in range(1, n // 2 + 1))
    sum_even = sum(evaluate_function(func_str, a + 2 * i * h) for i in range(1, n // 2))
    return h / 3 * (evaluate_function(func_str, a) + evaluate_function(func_str, b) + 
                    4 * sum_odd + 2 * sum_even)


def calculate_integral(method, func, a, b, eps, max_iter=1000000):
    """Calculating an integral with a given accuracy"""

    if a > b:
         a, b = b, a

    if method == "simpson":
         method = simpson
    elif method == "trapezoidal":
         method = trapezoidal
    elif method == "rectangle_mid":
         method = rectangle_mid
    elif method == "rectangle_left":
         method = rectangle_left
    elif method == "rectangle_right":
         method = rectangle_right
    else:
         raise NameError

    n = 4
    k = 2 if method != simpson else 4  # Order of accuracy of the method
    
    # First approximation
    I_prev = method(func, a, b, n)
    
    for _ in range(max_iter):
        n *= 2
        I_curr = method(func, a, b, n)
        
        if runge_rule(I_prev, I_curr, k, eps):
            return I_curr, n
        
        I_prev = I_curr

    
    raise ValueError(f"Требуемая точность не достигнута за {max_iter} итераций")
