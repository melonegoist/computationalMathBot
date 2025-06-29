import os
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, diff, solve, Eq, sin as sympy_sin, cos as sympy_cos, exp as sympy_exp, sqrt as sympy_sqrt
from gtts import gTTS
import logging
from typing import Dict, Tuple, List, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MathFunctionProcessor:
    """
    A class for processing mathematical functions with capabilities for:
    - Function analysis (roots, extrema, inflection points, asymptotes)
    - Graph generation
    - Text description generation
    - Text-to-speech conversion
    
    Attributes:
        x (Symbol): Sympy symbol for mathematical operations
        output_graph_dir (str): Directory path for saving graphs
        output_audio_dir (str): Directory path for saving audio files
    """
    
    def __init__(self):
        """Initialize the MathFunctionProcessor with default directories."""
        self.x = symbols('x')
        self.output_graph_dir = r"..\graphs"
        self.output_audio_dir = r"..\audio"

        os.makedirs(self.output_graph_dir, exist_ok=True)
        os.makedirs(self.output_audio_dir, exist_ok=True)

    def analyze_function(self, func_str: str) -> Dict[str, Union[str, List[float], Dict[str, List[str]]]]:
        """
        Analyze a mathematical function and return its properties.
        
        Args:
            func_str: String representation of the function (e.g., "x**2 + sin(x)")
            
        Returns:
            Dictionary containing:
            - type: Function type (trigonometric, polynomial, etc.)
            - derivative: First derivative as string
            - roots: List of real roots
            - extrema: List of critical points
            - inflection_points: List of inflection points
            - asymptotes: Dictionary of asymptote types
            - original_function: Original input string
            
        Raises:
            Exception: If function cannot be parsed or analyzed
        """
        try:
            # Replace ^ with ** for Python syntax and evaluate safely
            func_str = func_str.replace('^', '**')
            f = eval(func_str, {
                'x': self.x,
                'sin': sympy_sin,
                'cos': sympy_cos,
                'exp': sympy_exp,
                'sqrt': sympy_sqrt,
                'pi': np.pi
            })
            
            func_type = self._determine_function_type(f)
            
            return {
                'type': func_type,
                'derivative': str(diff(f, self.x)),
                'roots': self._find_roots(f),
                'extrema': self._find_extrema(f),
                'inflection_points': self._find_inflection_points(f),
                'asymptotes': self._find_asymptotes(f),
                'original_function': func_str
            }
            
        except Exception as e:
            logger.error(f"Error analyzing function: {e}")
            raise

    def _determine_function_type(self, f) -> str:
        """
        Classify the function type based on its components.
        
        Args:
            f: Sympy expression of the function
            
        Returns:
            String classification (trigonometric, cubic, quadratic, etc.)
        """
        f_str = str(f).lower()
        
        if any(t in f_str for t in ['sin', 'cos', 'tan']):
            return 'trigonometric'
        elif 'x**3' in f_str or 'x^3' in f_str:
            return 'cubic'
        elif 'x**2' in f_str or 'x^2' in f_str:
            return 'quadratic'
        elif 'exp' in f_str:
            return 'exponential'
        elif 'sqrt' in f_str:
            return 'irrational'
        elif 'x' in f_str and not ('**' in f_str or '^' in f_str):
            return 'linear'
        else:
            return 'algebraic'

    def _find_roots(self, f) -> Optional[List[float]]:
        """
        Find real roots of the function.
        
        Args:
            f: Sympy expression of the function
            
        Returns:
            List of real roots (up to 3) or None if not found
        """
        try:
            roots = solve(Eq(f, 0), self.x)
            return [float(r.evalf()) for r in roots if not r.is_imaginary][:3]
        except:
            return None

    def _find_extrema(self, f) -> Optional[List[float]]:
        """
        Find critical points (potential extrema) of the function.
        
        Args:
            f: Sympy expression of the function
            
        Returns:
            List of critical points (up to 3) or None if not found
        """
        try:
            f_prime = diff(f, self.x)
            critical_points = solve(Eq(f_prime, 0), self.x)
            return [float(cp.evalf()) for cp in critical_points if not cp.is_imaginary][:3]
        except:
            return None

    def _find_inflection_points(self, f) -> Optional[List[float]]:
        """
        Find inflection points of the function.
        
        Args:
            f: Sympy expression of the function
            
        Returns:
            List of inflection points (up to 3) or None if not found
        """
        try:
            f_double_prime = diff(f, self.x, 2)
            inflection_points = solve(Eq(f_double_prime, 0), self.x)
            return [float(ip.evalf()) for ip in inflection_points if not ip.is_imaginary][:3]
        except:
            return None

    def _find_asymptotes(self, f) -> Optional[Dict[str, List[str]]]:
        """
        Find vertical asymptotes of the function.
        
        Args:
            f: Sympy expression of the function
            
        Returns:
            Dictionary with 'vertical' key containing asymptote equations or None
        """
        try:
            denominator = f.as_numer_denom()[1]
            if denominator != 1:
                vertical_asymptotes = solve(Eq(denominator, 0), self.x)
                return {'vertical': [str(v) for v in vertical_asymptotes]}
            return None
        except:
            return None

    def generate_graph(self, func_str: str, analysis: Dict) -> str:
        """
        Generate and save a graph of the function with key points marked.
        
        Args:
            func_str: Original function string
            analysis: Dictionary from analyze_function()
            
        Returns:
            Path to the saved graph image
            
        Raises:
            Exception: If graph generation fails
        """
        try:
            # Determine appropriate x-range based on function type
            if analysis['type'] == 'trigonometric':
                x = np.linspace(-2*np.pi, 2*np.pi, 500)
            elif analysis['type'] == 'exponential':
                x = np.linspace(-2, 2, 500)
            else:
                x = np.linspace(-5, 5, 500)
            
            # Evaluate the function over the x-range
            y = eval(func_str.replace('^', '**'), {
                'x': x,
                'np': np,
                'sin': np.sin,
                'cos': np.cos,
                'exp': np.exp,
                'sqrt': np.sqrt,
                'pi': np.pi
            })
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            plt.plot(x, y, label=f"y = {func_str}")
            
            # Mark roots if they exist
            if analysis['roots']:
                for root in analysis['roots']:
                    if root is not None and min(x) <= root <= max(x):
                        plt.scatter(root, 0, color='red', zorder=5)
                        plt.text(root, 0, f' x={root:.2f}', verticalalignment='top')
            
            plt.title(f"Graph of: {func_str}\nType: {analysis['type']}")
            plt.xlabel('x')
            plt.ylabel('y')
            plt.grid(True)
            plt.legend()
            
            # Save the graph
            filename = os.path.join(self.output_graph_dir, f"graph_{func_str.replace('**', '^').replace('*', '')}.png")
            plt.savefig(filename, dpi=100)
            plt.close()
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating graph: {e}")
            raise

    def generate_text_description(self, analysis: Dict) -> str:
        """
        Generate a human-readable description of the function analysis.
        
        Args:
            analysis: Dictionary from analyze_function()
            
        Returns:
            Multiline string description of the function properties
        """
        try:
            description = f"Analysis of function {analysis['original_function']}:\n"
            description += f"Function type: {analysis['type']}\n"
            
            if analysis['roots']:
                description += f"Roots: {', '.join([f'{x:.2f}' for x in analysis['roots']])}\n"
            
            if analysis['extrema']:
                description += f"Extrema: {', '.join(f'{x:.2f}' for x in analysis['extrema'])}\n"
            
            if analysis['inflection_points']:
                description += f"Inflection points: {', '.join([f'{x:.2f}' for x in analysis['inflection_points']])}\n"
            
            if analysis['asymptotes'] and 'vertical' in analysis['asymptotes']:
                description += f"Vertical asymptotes: x = {'; x = '.join(analysis['asymptotes']['vertical'])}\n"
            
            description += f"Derivative: {analysis['derivative']}"
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            raise

    def text_to_speech(self, text: str, filename: str) -> str:
        """
        Convert text description to speech and save as MP3.
        
        Args:
            text: Text to convert
            filename: Output filename (without path)
            
        Returns:
            Path to the saved audio file
            
        Raises:
            Exception: If TTS conversion fails
        """
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            
            mp3_path = os.path.join(self.output_audio_dir, filename)
            tts.save(mp3_path)
            
            return mp3_path
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            raise

    def process_function(self, func_str: str) -> Tuple[str, str, str]:
        """
        Full processing pipeline for a mathematical function.
        
        Args:
            func_str: String representation of the function
            
        Returns:
            Tuple containing:
            - text_description: Analysis results as text
            - graph_path: Path to generated graph
            - audio_path: Path to generated audio description
            
        Raises:
            Exception: If any processing step fails
        """
        try:
            # 1. Analyze the function
            analysis = self.analyze_function(func_str)
            
            # 2. Generate text description
            description = self.generate_text_description(analysis)
            # Prepare text for speech (replace math symbols with words)
            audio_description = description.replace("**", " to the power of ").replace("*", " times ").replace("-", " minus ").replace("+", " plus ")
            
            # 3. Generate graph
            graph_path = self.generate_graph(func_str, analysis)
            
            # 4. Generate audio
            audio_path = self.text_to_speech(
                audio_description, 
                f"voice_main.mp3"
            )
            
            return description, graph_path, audio_path
            
        except Exception as e:
            logger.error(f"Error processing function {func_str}: {e}")
            raise


if __name__ == "__main__":
    """
    Example usage of the MathFunctionProcessor class.
    Processes several test functions and prints results.
    """
    processor = MathFunctionProcessor()
    
    functions = [
        "sin(x)",
        "x**3 - 2*x + 1",
        "x**2 - 4",
        "exp(x)",
        "sqrt(x + 3)",
        "1/(x - 2)"
    ]
    
    for func in functions:
        try:
            print(f"\nProcessing function: {func}")
            desc, graph, audio = processor.process_function(func)
            
            print(f"Text description:\n{desc}")
            print(f"Graph saved to: {graph}")
            print(f"Audio file saved to: {audio}")
            
        except Exception as e:
            print(f"Error processing function {func}: {e}")
            