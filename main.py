from flask import Flask, request, jsonify
import re
from fractions import Fraction

app = Flask(__name__)

MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)

NUM = r"[+-]?\d+"

def extract_integers(text):
    return [int(x) for x in re.findall(NUM, text)]

def format_number(value):
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        as_float = float(value)
        text = f"{as_float:.15f}".rstrip("0").rstrip(".")
        return text
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.15f}".rstrip("0").rstrip(".")
        return text
    return str(value)

def focus_text(query):
    q = query.lower()
    markers = [
        "actual task:",
        "task:",
        "question:",
        "solve:",
        "compute:",
        "calculate:",
        "find:",
    ]
    best_idx = -1
    best_len = 0
    for marker in markers:
        idx = q.rfind(marker)
        if idx > best_idx:
            best_idx = idx
            best_len = len(marker)
    if best_idx != -1:
        return q[best_idx + best_len :].strip()
    return q

def extract_date(text):
    pattern = rf"\b\d{{1,2}}\s(?:{MONTHS})\s\d{{4}}\b"
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(0) if m else None

def is_odd_even_query(q):
    return ("odd" in q or "even" in q) and any(w in q for w in ["is", "number", "numbers", "check", "odd?", "even?"])

def is_sum_even_query(q):
    q = q.lower()
    return "even" in q and any(w in q for w in ["sum", "total", "add"])

def is_sum_odd_query(q):
    q = q.lower()
    return "odd" in q and any(w in q for w in ["sum", "total", "add"])

def compute_binary_expression(text):
    q = text.lower()

    patterns = [
        # subtract 5 from 12
        (rf"\bsubtract\s+({NUM})\s+from\s+({NUM})\b", lambda m: Fraction(int(m.group(2))) - Fraction(int(m.group(1)))),
        # divide 20 by 4
        (rf"\bdivide\s+({NUM})\s+by\s+({NUM})\b", lambda m: Fraction(int(m.group(1))) / Fraction(int(m.group(2)))),
        # multiply 6 by 7
        (rf"\bmultiply\s+({NUM})\s+by\s+({NUM})\b", lambda m: Fraction(int(m.group(1))) * Fraction(int(m.group(2)))),
        # 13 + 7 / 13 plus 7 / 13 minus 7 / 13 times 7 / 13 x 7
        (rf"({NUM})\s*(?:\+|plus|added to)\s*({NUM})", lambda m: Fraction(int(m.group(1))) + Fraction(int(m.group(2)))),
        (rf"({NUM})\s*(?:-|minus|less)\s*({NUM})", lambda m: Fraction(int(m.group(1))) - Fraction(int(m.group(2)))),
        (rf"({NUM})\s*(?:\*|x|times|multiplied by)\s*({NUM})", lambda m: Fraction(int(m.group(1))) * Fraction(int(m.group(2)))),
        (rf"({NUM})\s*(?:/|divided by|over)\s*({NUM})", lambda m: Fraction(int(m.group(1))) / Fraction(int(m.group(2)))),
    ]

    for pattern, fn in patterns:
        m = re.search(pattern, q, re.IGNORECASE)
        if m:
            return fn(m)

    return None

def compute_sum_query(text):
    q = text.lower()
    nums = extract_integers(text)

    if not nums:
        return None

    if is_sum_even_query(q):
        return sum(n for n in nums if n % 2 == 0)

    if is_sum_odd_query(q):
        return sum(n for n in nums if n % 2 != 0)

    if any(w in q for w in ["sum", "add", "total"]):
        return sum(nums)

    return None

@app.route("/v1/answer", methods=["POST"])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query = str(data.get("query", ""))

        # Work on a focused slice if the prompt contains instruction noise.
        q = focus_text(query)
        full_q = query.lower()

        # Date extraction
        date_value = extract_date(query)
        if date_value:
            return jsonify({"output": date_value})

        # Odd/even YES/NO
        if "odd" in full_q and "number" in full_q:
            nums = extract_integers(query)
            if nums:
                return jsonify({"output": "YES" if nums[0] % 2 != 0 else "NO"})

        if "even" in full_q and "number" in full_q:
            nums = extract_integers(query)
            if nums:
                return jsonify({"output": "YES" if nums[0] % 2 == 0 else "NO"})

        # Sum of even/odd numbers
        sum_value = compute_sum_query(q)
        if sum_value is not None:
            return jsonify({"output": format_number(sum_value)})

        # Direct binary arithmetic from the focused text
        value = compute_binary_expression(q)
        if value is not None:
            return jsonify({"output": format_number(value)})

        # Fallback: try the full query for direct arithmetic
        value = compute_binary_expression(query)
        if value is not None:
            return jsonify({"output": format_number(value)})

        # Safe final fallback
        return jsonify({"output": "0"})

    except Exception:
        return jsonify({"output": "0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
