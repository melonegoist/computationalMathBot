import numpy as np

def is_diagonally(matrix: np.ndarray) -> bool:
    """
    Checks if a matrix is strictly diagonally dominant.
    
    A matrix is strictly diagonally dominant if for each row, the absolute value 
    of the diagonal element is greater than the sum of absolute values of other elements in that row.
    
    Args:
        matrix: Square numpy array representing the matrix
        
    Returns:
        bool: True if matrix is diagonally dominant, False otherwise
    """
    n = len(matrix)

    for i in range(n):
        # Calculate sum of absolute values of non-diagonal elements in current row
        row_sum = sum(abs(matrix[i][j]) for j in range(n) if j != i)

        # Check diagonal dominance condition
        if abs(matrix[i][i]) <= row_sum:
            return False
        
    return True


def rearrange_for_diagonal(matrix: np.ndarray) -> np.ndarray:
    """
    Attempts to rearrange matrix rows to achieve diagonal dominance.
    
    For each row, finds the row with maximum absolute value in the current column
    and swaps rows if necessary to put larger values on the diagonal.
    
    Args:
        matrix: Square numpy array representing the matrix
        
    Returns:
        np.ndarray: Rearranged matrix (may or may not be diagonally dominant)
    """
    n = len(matrix)

    for i in range(n):
        # Find row with maximum absolute value in current column (from current row downwards)
        max_row = max(range(i, n), key=lambda r: abs(matrix[r][i]))

        # Swap current row with max_row if different
        if i != max_row:
            matrix[i], matrix[max_row] = matrix[max_row], matrix[i]

    return matrix


def find_system_of_linear_equations_roots(matrix: list, accuracy: float) -> str:
    """
    Solves system of linear equations using iterative method with given accuracy.
    
    Implements Jacobi iteration method for solving linear systems. First attempts to make
    the matrix diagonally dominant for better convergence.
    
    Args:
        matrix: Augmented matrix of the system [A|B] where each row contains coefficients
               followed by the constant term
        accuracy: Desired accuracy threshold for stopping iterations
        
    Returns:
        str: Formatted string with HTML-like tags containing:
             - Matrix norm
             - Solution vector
             - Iteration count
             - Error progression
             Or warning message if matrix cannot be made diagonally dominant
    """
    n = len(matrix)

    # Split matrix into coefficient matrix A and constants vector B
    A = np.array([row[:-1] for row in matrix], dtype=float)
    B = np.array([row[-1] for row in matrix], dtype=float)
    
    # Try to make matrix diagonally dominant
    if not is_diagonally(A):
        A = rearrange_for_diagonal(A)

        # If still not diagonally dominant, return warning
        if not is_diagonally(A):
            return "non_diag_matrix_warning_message"
    
    # Initialize solution vector with zeros
    x = np.zeros(n)

    iterations = 0
    errors = []
    errors_output = ""
    
    # Iterative process
    while True:
        x_new = np.zeros(n)

        # Jacobi iteration: compute each component of new approximation
        for i in range(n):
            # Sum of products of known elements before current diagonal
            s1 = np.dot(A[i, :i], x[:i])
            # Sum of products of known elements after current diagonal
            s2 = np.dot(A[i, i+1:], x[i+1:])

            # Compute new value for current variable
            x_new[i] = (B[i] - s1 - s2) / A[i, i]
        
        # Calculate maximum error between iterations
        error = np.linalg.norm(x_new - x, np.inf)
        errors_output += str(float(error))+"\n" 
        errors.append(str(float(error))+"\n")

        iterations += 1
        
        # Stop if desired accuracy achieved
        if error < accuracy:
            break
        
        x = x_new

    # Calculate matrix norm (infinity norm)
    norm_A = np.linalg.norm(A, np.inf)

    # Format output string with results
    output = f"<b>Calculation results:</b>\n\n🔸 <i>Норма матрицы:</i> {norm_A}\n\n<i>🔸 Вектор неизвестных:</i>\n<pre>{x_new}</pre>\n\n<i>🔸 Количество итераций:</i> {iterations}\n\n<i>🔸 Вектор погрешностей:</i>\n<pre>{errors_output}</pre>"

    return output
