from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

# ─────────────────────────────────────────
# LEVEL 11: GCD of Polynomials
# ─────────────────────────────────────────
def solve_gcd_polynomial(q):
    try:
        # Find all (x−N) or (x-N) patterns for each polynomial definition
        # We look for p(x) = ... and q(x) = ...
        # Split on q(x) to separate the two polynomials
        q_lower = q

        # Extract p(x) line and q(x) line
        p_match = re.search(r"p\(x\)\s*=\s*([\s\S]+?)q\(x\)", q_lower)
        q_match = re.search(r"q\(x\)\s*=\s*([\s\S]+?)(?:Compute|$)", q_lower)

        if not p_match or not q_match:
            return "0"

        p_expr = p_match.group(1)
        q_expr = q_match.group(1)

        # Extract all roots from (x−N) or (x-N) or (x+N)
        def extract_roots(expr):
            # Match (x - N), (x−N), (x + N)
            roots = []
            # Handle unicode minus sign too
            expr = expr.replace("−", "-").replace("–", "-")
            for m in re.finditer(r"\(\s*x\s*([-+])\s*(\d+)\s*\)", expr):
                sign = m.group(1)
                val  = int(m.group(2))
                # (x - N) → root is +N
                # (x + N) → root is -N
                root = val if sign == "-" else -val
                roots.append(root)
            return set(roots)

        p_roots = extract_roots(p_expr)
        q_roots = extract_roots(q_expr)

        common = p_roots & q_roots
        return str(len(common))

    except Exception as e:
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

    # Level 11 — GCD polynomial
    if "gcd" in query.lower() and "polynomial" in query.lower():
        return jsonify({"output": solve_gcd_polynomial(query)})

    # Level 8 — Transaction log
    if "transaction" in query.lower() and "log" in query.lower():
        return jsonify({"output": solve_transaction(query)})

    # Level 7 — Rule-based
    if "Rule" in query or "rules" in query.lower():
        return jsonify({"output": solve_rules(query)})

    # Level 1-6 — Basic math
    val = solve_math(query)
    return jsonify({"output": f"The sum is {val}."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
