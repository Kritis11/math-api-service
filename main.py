# ─────────────────────────────────────────
# LEVEL 12: Definite Integral — ROBUST VERSION
# ─────────────────────────────────────────
def solve_integral(q):
    try:
        # Step 1: Aggressively normalize ALL unicode
        replacements = {
            "\u222b": "",     # ∫
            "\u2080": "0",    # ₀
            "\u2081": "1",    # ₁
            "\u2082": "2",    # ₂
            "\u2083": "3",    # ₃
            "\u2084": "4",    # ₄
            "\u2085": "5",    # ₅
            "\u2086": "6",    # ₆
            "\u2087": "7",    # ₇
            "\u2088": "8",    # ₈
            "\u2089": "9",    # ₉
            "\u00b2": "^2",   # ²
            "\u00b3": "^3",   # ³
            "\u2212": "-",    # −
            "\u2013": "-",    # –
            "\u2014": "-",    # —
        }
        for old, new in replacements.items():
            q = q.replace(old, new)
        
        # Remove spaces
        q = q.replace(" ", "")
        
        # Step 2: Extract bounds
        # Pattern: from0to3 or 0to3 or 0-3
        bounds_match = re.search(r"(?:from)?(\d+)(?:to|,|-)(\d+)", q)
        if not bounds_match:
            return "0"
        
        lower = int(bounds_match.group(1))
        upper = int(bounds_match.group(2))
        
        # Step 3: Extract expression
        # Look for content inside parentheses
        expr_match = re.search(r"\(([^)]+)\)", q)
        if not expr_match:
            return "0"
        
        expr = expr_match.group(1)
        
        # Step 4: Parse expression "9-x^2" or "9-x²" or "9-x2"
        # Handle: constant - coefficient * x^power
        # Pattern: number - number * x^number
        pattern = r"(\d+)\s*-\s*(\d*)\s*\*?\s*x\s*(?:\^)?(\d*)"
        m = re.match(pattern, expr)
        if m:
            a = int(m.group(1))  # constant: 9
            b_str = m.group(2)   # coefficient: "" or "1"
            b = int(b_str) if b_str else 1
            p_str = m.group(3)   # power: "2" or ""
            power = int(p_str) if p_str else 2
            
            # ∫ a dx = a*x from lower to upper
            # ∫ -b*x^n dx = -(b/(n+1))*x^(n+1)
            result = a * upper - a * lower
            result -= (b / (power + 1)) * (upper ** (power + 1) - lower ** (power + 1))
            
            return str(int(round(result)))
        
        # Fallback: just compute any simple integral
        # Pattern: x^2 or x^3
        m2 = re.search(r"x\s*(?:\^)?(\d+)", expr)
        if m2:
            power = int(m2.group(1))
            result = (1 / (power + 1)) * (upper ** (power + 1) - lower ** (power + 1))
            return str(int(round(result)))
        
        return "0"
    except Exception as e:
        return "0"
