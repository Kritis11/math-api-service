from flask import Flask, request, jsonify
import re
import os
import unicodedata

app = Flask(__name__)


# ─────────────────────────────────────────
# LEVEL 12: Definite Integral
# ─────────────────────────────────────────
def solve_integral(q):
    try:
        q = unicodedata.normalize("NFKC", q)
        translation = str.maketrans({
            "\u2212": "-",
            "\u2013": "-",
            "\u2014": "-",
            "\u00b2": "^2",
            "\u00b3": "^3",
            "\u2074": "^4",
            "\u2075": "^5",
            "\u2076": "^6",
            "\u2077": "^7",
            "\u2078": "^8",
            "\u2079": "^9",
            "\u2070": "^0",
            "\u2080": "0",
            "\u2081": "1",
            "\u2082": "2",
            "\u2083": "3",
            "\u2084": "4",
            "\u2085": "5",
            "\u2086": "6",
            "\u2087": "7",
            "\u2088": "8",
            "\u2089": "9",
            "\u222b": "",
            "\u00b7": "*",
            "\u00d7": "*",
        })
        q = q.translate(translation)

        compact = re.sub(r"\s+", "", q)

        bounds = re.search(r"(?:from)?(-?\d+)(?:to)(-?\d+)", compact, re.I)
        if bounds:
            lower = int(bounds.group(1))
            upper = int(bounds.group(2))
        else:
            digits = re.findall(r"-?\d+", compact[:30])
            if len(digits) >= 2:
                lower = int(digits[0])
                upper = int(digits[1])
            else:
                return "0"

        expr_match = re.search(r"\(([^()]*)\)", compact)
        expr = expr_match.group(1) if expr_match else compact

        expr = expr.replace("^", "**")
        expr = expr.replace("-", "+-")
        terms = [t for t in expr.split("+") if t.strip()]

        def integrate_term(term, x):
            term = term.strip()
            if not term:
                return 0.0
            term = term.replace(" ", "").replace("*", "")
            if "x" not in term:
                try:
                    return float(term) * x
                except Exception:
                    return 0.0
            if "x**" in term:
                parts = term.split("x**", 1)
                coef_str = parts[0]
                power = int(parts[1])
            else:
                parts = term.split("x", 1)
                coef_str = parts[0]
                power = 1
            if coef_str in ("", "+"):
                coef = 1.0
            elif coef_str == "-":
                coef = -1.0
            else:
                try:
                    coef = float(coef_str)
                except Exception:
                    coef = 1.0
            return coef / (power + 1) * (x ** (power + 1))

        upper_val = sum(integrate_term(t, upper) for t in terms)
        lower_val = sum(integrate_term(t, lower) for t in terms)
        result = upper_val - lower_val

        if abs(result - round(result)) < 1e-9:
            return str(int(round(result)))
        return str(round(result, 6))

    except Exception:
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
                val = int(m.group(2))
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
# LEVEL 1-6: Basic Math
# ─────────────────────────────────────────
def solve_math(q):
    try:
        nums = re.findall(r"-?\d+", q)
        if not nums:
            return "0"
        nums = [int(n) for n in nums]
        ql = q.lower()
        if any(op in ql for op in ["minus", "subtract"]):
            return str(nums[0] - nums[1]) if len(nums) >= 2 else str(nums[0])
        if any(op in ql for op in ["times", "multipl", "product"]):
            result = 1
            for n in nums:
                result *= n
            return str(result)
        if any(op in ql for op in ["divided", "divide"]):
            return str(nums[0] // nums[1]) if len(nums) >= 2 else str(nums[0])
        return str(sum(nums))
    except Exception:
        return "0"


# ─────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────
@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")

    if not isinstance(query, str) or not query.strip():
        return jsonify({"output": "0"})

    ql = query.lower()

    # Level 12 — Definite Integral
    if "integral" in ql or "\u222b" in query:
        return jsonify({"output": solve_integral(query)})

    # Level 11 — GCD Polynomial
    if "gcd" in ql and "polynomial" in ql:
        return jsonify({"output": solve_gcd_polynomial(query)})

    # Level 1-6 — Basic Math
    val = solve_math(query)
    return jsonify({"output": "The sum is " + val + "."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
