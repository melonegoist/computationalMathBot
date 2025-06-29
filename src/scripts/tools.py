from math import sin, cos, exp, log, sqrt
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os


def parse_equations(equation: str):
    """
    Parses a string with equations of the form "x**2 + y = 4; y = sin(x)".
    Returns the function F(x, y) = [f1(x, y), f2(x, y), ...],

    """

    equations = [eq.strip() for eq in equation.split(';') if eq.strip()]
    
    parsed_equations = []
    for eq in equations:
        if '=' in eq:
            left, right = eq.split('=', 1)
            parsed_eq = f"({left}) - ({right})"
        else:
            parsed_eq = eq

        parsed_equations.append(parsed_eq)
    
    def F(x, y):
        try:
            allowed_names = {'x': x, 'y': y, 
                            'sin': sin, 'cos': cos, 'exp': exp, 
                            'log': log, 'sqrt': sqrt, 'abs': abs}
            
            return [eval(eq, {'__builtins__': None}, allowed_names) for eq in parsed_equations]

        except Exception as e:
            raise ValueError(f"Error when evaluating equation: {str(e)}")
    
    return F


def parse_single_argument_equation(equation: str):
    """
    Parses a string with an equation like "x**2 + 3 = 4" or "sin(x) + cos(x)".
    Returns a function f(x) that evaluates the expression.

    Usage examples:
    >>> f = parse_single_argument_equation("x**2 - 4")
    >>> f(2) # returns 0 (2² - 4 = 0)
    >>> f = parse_single_argument_equation("sin(x) + cos(x)")
    >>> f(0) # returns 1 (sin(0) + cos(0) = 0 + 1 = 1)
    """

    # Remove spaces and check for the equal sign
    equation = equation.strip()
    if '=' in equation:
        left, right = equation.split('=', 1)
        parsed_eq = f"({left.strip()}) - ({right.strip()})"
    else:
        parsed_eq = equation
    
    def f(x):
        try:
            allowed_names = {
                'x': x,
                'sin': sin, 'cos': cos, 'tan': lambda x: sin(x)/cos(x),
                'exp': exp, 'log': log, 'sqrt': sqrt,
                'pi': 3.141592653589793
            }
            return eval(parsed_eq, {'__builtins__': None}, allowed_names)
        except Exception as e:
            raise ValueError(f"Error in calculating the equation '{equation}': {str(e)}")
    
    return f



def plot_function_with_highlight(equation, highlight_xmin, highlight_xmax, 
                               total_xmin=None, total_xmax=None, num_points=1000):
    """
    Visualization of the function graph with the specified interval highlighted.

    Parameters:
    - equation: function to plot (e.g. lambda x: np.sin(x))
    - highlight_xmin, highlight_xmax: interval to highlight
    - total_xmin, total_xmax: total range to display (if None, determined automatically)
    - num_points: number of points to plot
    """

    equation = parse_single_argument_equation(equation)

    # Если полный диапазон не указан, расширяем выделенный интервал на 25% в обе стороны
    if total_xmin is None:
        total_xmin = highlight_xmin - 0.25*(highlight_xmax - highlight_xmin)
    if total_xmax is None:
        total_xmax = highlight_xmax + 0.25*(highlight_xmax - highlight_xmin)
    
    # Create arrays of values
    x_total = np.linspace(total_xmin, total_xmax, num_points)
    x_highlight = np.linspace(highlight_xmin, highlight_xmax, num_points)
    
    # Calculate y-values
    y_total = equation(x_total)
    y_highlight = equation(x_highlight)
    
    # Create a graph
    plt.figure(figsize=(12, 6))
    
    # Full schedule (pale)
    plt.plot(x_total, y_total, color='gray', alpha=0.5, label='Полный график')
    
    # Selected interval (bright)
    plt.plot(x_highlight, y_highlight, color='red', linewidth=2, label=f'Выделенный интервал [{highlight_xmin}, {highlight_xmax}]')

    # Add vertical lines for interval boundaries
    plt.axvline(x=highlight_xmin, color='blue', linestyle='--', alpha=0.7)
    plt.axvline(x=highlight_xmax, color='blue', linestyle='--', alpha=0.7)
    
    # Graph settings
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title(f'График функции с выделением интервала [{highlight_xmin}, {highlight_xmax}]')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Automatic y scaling
    plt.autoscale(enable=True, axis='y')

    current_dir = os.path.dirname(__file__)
    graph_path = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "graph_storage", "graph.png"))
    
    plt.savefig(graph_path, dpi=100, bbox_inches='tight')

    return Image.open(graph_path)
