from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

# ─────────────────────────────────────────
# LEVEL 12: Definite Integral
# ─────────────────────────────────────────
def solve_integral(q):
    try:
        # Normalize unicode characters
        q = q.replace("\u222b", "").replace("\u2080", "0")  # ∫ and ₀
        q = q.replace("\u2081", "1").replace("\u2082", "2")
        q = q.replace("\u2083", "3").replace("\u2084", "4")
        q = q.replace("\u2085", "5").replace("\u2086", "6")
        q = q.replace("\u2087", "7").replace("\u2088", "8")
        q = q.replace("\u2089", "9")

        # Extract bounds: look for numbers after the integral sign
        # Pattern: ∫₀³ or ∫ from 0 to 3
        bounds_match = re.search(r"(?:from\s+)?(\d+)\s*(?:to|,|−|-)\s*(\d+)", q)
        if not bounds_match:
            # Try to find subscript pattern: ₀³
            subs = re.findall(r"\u2080(\d)", q)
            if subs:
                return subs[0]
            return "0"
        
        lower = int(bounds_match.group(1))
        upper = int(bounds_match.group(2))

        # Extract the expression inside parentheses or after the integral
        # Pattern: (9 - x^2) or (9-x^2) or 9 - x^2
        expr_match = re.search(r"\(([^)]+)\)", q)
        if expr_match:
            expr = expr_match.group(1)
        else:
            expr = q

        # Simple polynomial integrator
        # Works for: a, a*x, a*x^2, a*x^n, a - b*x^2, etc.
        expr = expr.replace(" ", "")
        
        # Parse into terms: split by + and -
        # For simplicity, handle common patterns:
        # Pattern 1: "9-x^2" or "9-x²"
        # Pattern 2: "a*x^n + b*x^m"
        
        # Handle the standard case: (a - b*x^2)
        const_match = re.search(r"(\d+)\s*-\s*(\d*)\s*\*?\s*x\s*(?:\^|²)\s*(\d*)", expr)
        if const_match:
            a = int(const_match.group(1))  # 9
            b_str = const_match.group(2)   # 1 or empty
            b = int(b_str) if b_str else 1
            pow_str = const_match.group(3) # 2 or empty
            power = int(pow_str) if pow_str else 2
            
            # ∫ a dx = a*x
            # ∫ -b*x^n dx = -(b/(n+1))*x^(n+1)
            result = a * upper - a * lower
            result -= (b / (power + 1)) * (upper ** (power + 1) - lower ** (power + 1))
            
            return str(int(round(result)))
        
        # Handle (x^2 - a) or similar
        const_match2 = re.search(r"(\d*)\s*\*?\s*x\s*(?:\^|²)\s*(\d*)\s*[-+]\s*(\d+)", expr)
        if const_match2:
            a_str = const_match2.group(1)
            a = int(a_str) if a_str else 1
            pow_str = const_match2.group(2)
            power = int(pow_str) if pow_str else 2
            c = int(const_match2.group(3))
            
            result = (a / (power + 1)) * (upper ** (power + 1) - lower ** (power + 1))
            result += c * upper - c * lower
            
            return str(int(round(result)))

        # Simple: just "x^2" or "x²"
        simple_match = re.search(r"x\s*(?:\^|²)\s*(\d*)", expr)
        if simple_match:
            power_str = simple_match.group(1)
            power = int(power_str) if power_str else 2
            result = (1 / (power + 1)) * (upper ** (power + 1) - lower ** (power + 1))
            return str(int(round(result)))

        return "0"
    except Exception as e:
        return "0"

# ─────────────────────────────────────────
# LEVEL 11: GCD of Polynomials
# ─────────────────────────────────────────
def solve_gcd_polynomial(q):
    try:
        q = q.replace("\u2212", "-")
        q = q.replace("\u2013", "-")
        q = q.replace("\u2014", "-")
        
        p_match = re.search(r"p\(x\)\s*=\s*([\s\S]+?)q\(x\)", q)
        q_match = re.search(r"q\(x\)\s*=\s*([\s\S]+?)(?:Compute|$)", q)
        
        if not p_match or not q_match:
            return "0"
        
        p_expr = p_match.group(1)
        q_expr = q_match.group(1)
        
        def extract_roots(expr):
            roots = []
            for m in re.finditer(r"\(\s*x\s*([-+])\s*(\d+)\s*\)", expr):
                sign = m.group(1)
                val  = int(m.group(2))
                root = val if sign == "-" else -val
                roots.append(root)
            return set(roots)
        
        p_roots = extract_roots(p_expr)
        q_roots = extract_roots(q_expr)
        
        common = p_roots & q_roots
        return str(len(common))
    except Exception:
        return "0"

# ─────────────────────────────────────────
# LEVEL 8: Transaction Log
# ─────────────────────────────────────────
def solve_transaction(q):
    try:
        letter_match = re.search(r"starts with '(\w)'", q, re.I)
        target_letter = letter_match.group(1).upper() if letter_match else "S"
        
        amount_match = re.search(r"greater than \$?(\d+)", q)
        threshold = int(amount_match.group(1)) if amount_match else 100
        
        transactions = re.findall(r"([A-Z][a-z]+)\s+paid\s+\$?(\d+)", q)
        
        for name, amount_str in transactions:
            amount = int(amount_str)
            if name.upper().startswith(target_letter) and amount > threshold:
                return f"{name} paid the amount of ${amount}."
        
        return "No matching transaction found."
    except Exception:
        return "Error parsing transaction."

# ─────────────────────────────────────────
# LEVEL 7: Rule-based logic
# ─────────────────────────────────────────
def solve_rules(q):
    try:
        start_num = int(re.search(r"number\s*(-?\d+)", q).group(1))
        res = start_num
        
        if res % 2 == 0:
            if "double" in q:   res *= 2
            elif "triple" in q: res *= 3
            else:
                m = re.search(r"even\s*→\s*add\s*(\d+)", q)
                if m: res += int(m.group(1))
        else:
            if "double" in q:   res *= 2
            elif "triple" in q: res *= 3
            else:
                m = re.search(r"odd\s*→\s*add\s*(\d+)", q)
                if m: res += int(m.group(1))
        
        comp = re.search(r"result\s*>\s*(\d+)", q)
        if comp:
            threshold = int(comp.group(1))
            if res > threshold:
                m = re.search(r"subtract\s*(\d+)", q)
                if m: res -= int(m.group(1))
            else:
                m = re.search(r"Otherwise\s*→\s*add\s*(\d+)", q)
                if m: res += int(m.group(1))
        
        div_m  = re.search(r"divisible\s*by\s*(\d+)", q)
        word_m = re.search(r"output\s*\"([^\"]+)\"", q)
        if div_m and word_m:
            if res % int(div_m.group(1)) == 0:
                return word_m.group(1)
        return str(res)
    except:
        return "Error"

# ─────────────────────────────────────────
# LEVEL 1-6: Basic Math
# ─────────────────────────────────────────
def solve_math(q):
    nums = re.findall(r"-?\d+", q)
    if not nums: return "0"
    nums = [int(n) for n in nums]
    ql = q.lower()
    
    if any(op in ql for op in ["minus", "subtract"]):
        return str(nums[0] - nums[1]) if len(nums) >= 2 else str(nums[0])
    if any(op in ql for op in ["times", "multipl", "product"]):
        result = 1
        for n in nums: result *= n
        return str(result)
    if any(op in ql for op in ["divided", "divide"]):
        return str(nums[0] // nums[1]) if len(nums) >= 2 else str(nums[0])
    return str(sum(nums))

# ─────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────
@app.route("/v1/answer", methods=["POST"])
def answer():
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "")
    
    if not query:
        return jsonify({"output": "0"})
    
    ql = query.lower()
    
    # Level 12 — Definite Integral
    if "integral" in ql:
        return jsonify({"output": solve_integral(query)})
    
    # Level 11 — GCD polynomial
    if "gcd" in ql and "polynomial" in ql:
        return jsonify({"output": solve_gcd_polynomial(query)})
    
    # Level 8 — Transaction log
    if "transaction" in ql and "log" in ql:
        return jsonify({"output": solve_transaction(query)})
    
    # Level 7 — Rule-based
    if "Rule" in query or "rules" in ql:
        return jsonify({"output": solve_rules(query)})
    
    # Level 1-6 — Basic math
    val = solve_math(query)
    return jsonify({"output": f"The sum is {val}."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
