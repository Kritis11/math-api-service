import re
import math
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================================
# SOLVER 1: Modular Exponentiation (Last X digits of Y^Z)
# ============================================================================
def solve_modular_exp(q):
    """
    Handles:
    - "What are the last 6 digits of 7^777?"
    - "7^777 mod 10^6"
    - "compute 7^777 mod 10^6"
    """
    ql = q.lower()
    
    # Pattern 1: "last X digits of Y^Z"
    m = re.search(r'last\s+(\d+)\s+digits?\s+of\s+(\d+)\s*\^\s*(\d+)', ql)
    if m:
        digits = int(m.group(1))
        base = int(m.group(2))
        exp = int(m.group(3))
        mod = 10 ** digits
        result = pow(base, exp, mod)
        
        # Format with leading zeros if needed
        s = str(result)
        if len(s) < digits:
            s = s.zfill(digits)
        return s
    
    # Pattern 2: "Y^Z mod 10^X"
    m = re.search(r'(\d+)\s*\^\s*(\d+)\s+mod\s+10\s*\^\s*(\d+)', ql)
    if m:
        base = int(m.group(1))
        exp = int(m.group(2))
        mod_pow = int(m.group(3))
        mod = 10 ** mod_pow
        result = pow(base, exp, mod)
        
        s = str(result)
        if len(s) < mod_pow:
            s = s.zfill(mod_pow)
        return s
    
    return None


# ============================================================================
# SOLVER 2: Definite Integrals
# ============================================================================
def solve_integral(q):
    """
    Handles:
    - "Compute the definite integral from 0 to 3 of (9 minus x squared) dx"
    - "∫₀³ (9 − x²) dx"
    - Uses numerical integration (Simpson's rule)
    """
    ql = q.lower()
    
    # Check if it's an integral query
    if 'integral' not in ql and '∫' not in ql:
        return None
    
    try:
        # Replace word-based operations
        q_clean = q.lower()
        q_clean = q_clean.replace('minus', '-')
        q_clean = q_clean.replace('plus', '+')
        q_clean = q_clean.replace('times', '*')
        q_clean = q_clean.replace('divided by', '/')
        q_clean = q_clean.replace('squared', '^2')
        q_clean = q_clean.replace('cubed', '^3')
        q_clean = q_clean.replace('^', '**')
        q_clean = q_clean.replace('−', '-')  # Unicode minus
        
        # Extract bounds: "from X to Y" or "₀³"
        bounds_match = re.search(r'from\s+([-\d.]+)\s+to\s+([-\d.]+)', q_clean)
        if not bounds_match:
            bounds_match = re.search(r'integral\s*[:\s]*.*?([0-9\-]+).*?to.*?([0-9\-]+)', q_clean)
        if not bounds_match:
            # Try digit extraction
            digits = re.findall(r'[-]?\d+\.?\d*', q_clean)
            if len(digits) >= 2:
                a, b = float(digits[0]), float(digits[1])
            else:
                return None
        else:
            a = float(bounds_match.group(1))
            b = float(bounds_match.group(2))
        
        # Extract integrand: between "of" and "dx"
        integrand_match = re.search(r'of\s+(.*?)\s+dx', q_clean)
        if not integrand_match:
            integrand_match = re.search(r'\((.*?)\)\s*dx', q_clean)
        
        if not integrand_match:
            return None
        
        integrand_str = integrand_match.group(1).strip()
        
        # Clean up integrand
        integrand_str = integrand_str.replace('(', '').replace(')', '')
        integrand_str = integrand_str.strip()
        
        # Simpson's rule for numerical integration
        def simpson_rule(f, a, b, n=1000):
            h = (b - a) / n
            x = a
            result = f(a) + f(b)
            for i in range(1, n):
                x = a + i * h
                if i % 2 == 1:
                    result += 4 * f(x)
                else:
                    result += 2 * f(x)
            result *= h / 3.0
            return result
        
        # Create function from string
        def f(x):
            expr = integrand_str.replace('x', f'({x})')
            try:
                return eval(expr)
            except:
                return 0
        
        result = simpson_rule(f, a, b)
        result_int = int(round(result))
        
        return str(result_int)
    
    except Exception as e:
        return None


# ============================================================================
# SOLVER 3: Basic Arithmetic (sum, difference, product, quotient)
# ============================================================================
def solve_arithmetic(q):
    """
    Handles:
    - "What is 5 plus 3?"
    - "5 + 3"
    - "compute 10 times 2 divided by 4"
    - Supports: plus, minus, times, divided by, sum, difference, product
    """
    ql = q.lower()
    
    # Remove common question words
    q_clean = ql.replace('what is', '').replace('compute', '').replace('calculate', '')
    q_clean = q_clean.replace('the sum is', '').replace('output only the integer', '')
    q_clean = q_clean.replace('output only', '').replace('?', '').strip()
    
    # Replace word operators with symbols
    q_clean = re.sub(r'\bdivided\s+by\b', '/', q_clean)
    q_clean = re.sub(r'\btimes\b', '*', q_clean)
    q_clean = re.sub(r'\bplus\b', '+', q_clean)
    q_clean = re.sub(r'\bminus\b', '-', q_clean)
    
    # Handle "sum of X and Y" pattern
    sum_match = re.search(r'sum\s+(?:of\s+)?([^?]+?)(?:\s+and\s+|\+)([^?]+)', q_clean)
    if sum_match:
        try:
            a = float(sum_match.group(1).strip())
            b = float(sum_match.group(2).strip())
            result = int(a + b)
            return str(result)
        except:
            pass
    
    # Extract all numbers
    numbers = re.findall(r'-?\d+\.?\d*', q_clean)
    if not numbers:
        return None
    
    try:
        # Convert to floats
        numbers = [float(n) for n in numbers]
        
        # Determine operation from keywords
        if '+' in q_clean or 'plus' in ql or 'sum' in ql:
            result = sum(numbers)
        elif '*' in q_clean or 'times' in ql or 'product' in ql:
            result = 1
            for n in numbers:
                result *= n
        elif '/' in q_clean or 'divided' in ql:
            result = numbers[0]
            for n in numbers[1:]:
                if n != 0:
                    result /= n
        elif '-' in q_clean or 'minus' in ql or 'difference' in ql:
            result = numbers[0]
            for n in numbers[1:]:
                result -= n
        else:
            # Default: sum
            result = sum(numbers)
        
        result_int = int(round(result))
        return str(result_int)
    
    except Exception as e:
        return None


# ============================================================================
# MAIN HANDLER
# ============================================================================
@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json()
        q = data.get('query', '')
        
        if not q:
            return jsonify({"output": "0"})
        
        # Try solvers in order of specificity
        
        # 1. Modular exponentiation (most specific)
        result = solve_modular_exp(q)
        if result is not None:
            return jsonify({"output": result})
        
        # 2. Definite integrals
        result = solve_integral(q)
        if result is not None:
            return jsonify({"output": result})
        
        # 3. Basic arithmetic (most general)
        result = solve_arithmetic(q)
        if result is not None:
            return jsonify({"output": result})
        
        # No solver matched
        return jsonify({"output": "0"})
    
    except Exception as e:
        return jsonify({"output": "0"})


# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
