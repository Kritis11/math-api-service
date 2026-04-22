from flask import Flask, request, jsonify
import re
from fractions import Fraction

app = Flask(__name__)

NUM = r"[+-]?\d+"
MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)

def extract_integers(text):
    return [int(x) for x in re.findall(NUM, text)]

def format_number(value):
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        text = f"{float(value):.15f}".rstrip("0").rstrip(".")
        return text if text else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.15f}".rstrip("0").rstrip(".")
        return text if text else "0"
    return str(value)

def normalize_text(text):
    return (
        text.replace("→", "->")
            .replace("“", '"')
            .replace("”", '"')
            .replace("’", "'")
    )

def is_exact_integer(value):
    return isinstance(value, int) or (isinstance(value, Fraction) and value.denominator == 1)

def as_fraction(value):
    if isinstance(value, Fraction):
        return value
    return Fraction(value)

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
        return query[best_idx + best_len:].strip()
    return query

def extract_date(text):
    pattern = rf"\b\d{{1,2}}\s(?:{MONTHS})\s\d{{4}}\b"
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(0) if m else None

def is_sum_even_query(q):
    q = q.lower()
    return "even" in q and any(w in q for w in ["sum", "total", "add"])

def is_sum_odd_query(q):
    q = q.lower()
    return "odd" in q and any(w in q for w in ["sum", "total", "add"])

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

def compute_binary_expression(text):
    q = text.lower()

    patterns = [
        (rf"\bsubtract\s+({NUM})\s+from\s+({NUM})\b",
         lambda m: Fraction(int(m.group(2))) - Fraction(int(m.group(1)))),

        (rf"\bdivide\s+({NUM})\s+by\s+({NUM})\b",
         lambda m: Fraction(int(m.group(1))) / Fraction(int(m.group(2)))),

        (rf"\bmultiply\s+({NUM})\s+by\s+({NUM})\b",
         lambda m: Fraction(int(m.group(1))) * Fraction(int(m.group(2)))),

        (rf"({NUM})\s*(?:\+|plus|added to)\s*({NUM})",
         lambda m: Fraction(int(m.group(1))) + Fraction(int(m.group(2)))),

        (rf"({NUM})\s*(?:-|minus|less)\s*({NUM})",
         lambda m: Fraction(int(m.group(1))) - Fraction(int(m.group(2)))),

        (rf"({NUM})\s*(?:\*|x|times|multiplied by)\s*({NUM})",
         lambda m: Fraction(int(m.group(1))) * Fraction(int(m.group(2)))),

        (rf"({NUM})\s*(?:/|divided by|over)\s*({NUM})",
         lambda m: Fraction(int(m.group(1))) / Fraction(int(m.group(2)))),
    ]

    for pattern, fn in patterns:
        m = re.search(pattern, q, re.IGNORECASE)
        if m:
            return fn(m)

    return None

def parse_action(action, value):
    action_raw = action.strip().strip(". ")
    a = action_raw.lower()

    m = re.search(r'output\s+"([^"]+)"', action_raw, re.IGNORECASE)
    if m:
        return ("TEXT", m.group(1))

    if re.search(r"\boutput\s+the\s+(?:number|result|value)\b", a):
        return ("NUMBER", value)

    if re.search(r"\bdouble\s+it\b", a):
        return as_fraction(value) * 2

    if re.search(r"\btriple\s+it\b", a):
        return as_fraction(value) * 3

    if re.search(r"\bhalve\s+it\b|\bhalf\s+it\b", a):
        return as_fraction(value) / 2

    if re.search(r"\bsquare\s+it\b", a):
        v = as_fraction(value)
        return v * v

    m = re.search(r"\badd\s+([+-]?\d+)\b", a)
    if m:
        return as_fraction(value) + int(m.group(1))

    m = re.search(r"\bsubtract\s+([+-]?\d+)\b", a)
    if m:
        return as_fraction(value) - int(m.group(1))

    m = re.search(r"\bmultiply\s+by\s+([+-]?\d+)\b", a)
    if m:
        return as_fraction(value) * int(m.group(1))

    m = re.search(r"\bdivide\s+by\s+([+-]?\d+)\b", a)
    if m:
        divisor = int(m.group(1))
        if divisor == 0:
            return as_fraction(value)
        return as_fraction(value) / divisor

    return as_fraction(value)

def check_condition(condition, value):
    c = condition.lower().strip().strip(". ")
    v = as_fraction(value)

    if re.search(r"\bodd\b", c) and "divisible by" not in c:
        return is_exact_integer(v) and (v.numerator % 2 != 0)

    if re.search(r"\beven\b", c) and "divisible by" not in c:
        return is_exact_integer(v) and (v.numerator % 2 == 0)

    m = re.search(r"\bdivisible\s+by\s+([+-]?\d+)\b", c)
    if m:
        d = int(m.group(1))
        if d == 0:
            return False
        return is_exact_integer(v) and (v.numerator % d == 0)

    m = re.search(r"(>=|<=|>|<|==|=)\s*([+-]?\d+)", c)
    if m:
        op = m.group(1)
        n = Fraction(int(m.group(2)))
        if op == ">":
            return v > n
        if op == "<":
            return v < n
        if op == ">=":
            return v >= n
        if op == "<=":
            return v <= n
        return v == n

    m = re.search(r"\bgreater\s+than\s+([+-]?\d+)\b", c)
    if m:
        return v > Fraction(int(m.group(1)))

    m = re.search(r"\bless\s+than\s+([+-]?\d+)\b", c)
    if m:
        return v < Fraction(int(m.group(1)))

    m = re.search(r"\bequal(?:s| to)?\s+([+-]?\d+)\b", c)
    if m:
        return v == Fraction(int(m.group(1)))

    return False

def execute_rule_segment(segment, value):
    s = normalize_text(segment).strip()

    # Pattern: If even -> X. If odd -> Y.
    m = re.search(
        r"if\s+even\s*->\s*(.*?)\s*\.\s*if\s+odd\s*->\s*(.*)",
        s,
        re.IGNORECASE | re.DOTALL
    )
    if m:
        chosen = m.group(1) if check_condition("even", value) else m.group(2)
        return parse_action(chosen, value)

    m = re.search(
        r"if\s+odd\s*->\s*(.*?)\s*\.\s*if\s+even\s*->\s*(.*)",
        s,
        re.IGNORECASE | re.DOTALL
    )
    if m:
        chosen = m.group(1) if check_condition("odd", value) else m.group(2)
        return parse_action(chosen, value)

    # Pattern: If condition -> X. Otherwise -> Y.
    parts = re.split(r"\botherwise\s*->\s*", s, flags=re.IGNORECASE, maxsplit=1)
    if_part = parts[0].strip()
    else_action = parts[1].strip() if len(parts) > 1 else None

    m = re.search(r"if\s+(.*?)\s*->\s*(.*)", if_part, re.IGNORECASE | re.DOTALL)
    if m:
        condition = m.group(1).strip()
        true_action = m.group(2).strip().strip(". ")
        if check_condition(condition, value):
            return parse_action(true_action, value)
        if else_action is not None:
            return parse_action(else_action.strip().strip(". "), value)

    return value

def solve_rule_engine(query):
    text = normalize_text(query)

    if "rule" not in text.lower():
        return None

    m = re.search(r"\binput\s+number\s+([+-]?\d+)\b", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\binput\s*[:=]?\s*([+-]?\d+)\b", text, re.IGNORECASE)
    if not m:
        return None

    current = Fraction(int(m.group(1)))

    parts = re.split(r"\brule\s*\d+\s*:", text, flags=re.IGNORECASE)
    rule_segments = [p.strip() for p in parts[1:] if p.strip()]
    if not rule_segments:
        return None

    for segment in rule_segments:
        result = execute_rule_segment(segment, current)

        if isinstance(result, tuple):
            kind, payload = result
            if kind == "TEXT":
                return payload
            if kind == "NUMBER":
                return format_number(payload)

        current = as_fraction(result)

    return format_number(current)

@app.route("/v1/answer", methods=["POST"])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query = str(data.get("query", ""))
        full_q = query.lower()
        focused = focus_text(query)

        # Level 7 rule engine
        rule_answer = solve_rule_engine(query)
        if rule_answer is not None:
            return jsonify({"output": str(rule_answer)})

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

        # Sum queries
        sum_value = compute_sum_query(focused)
        if sum_value is not None:
            return jsonify({"output": format_number(sum_value)})

        # Direct arithmetic from focused part
        value = compute_binary_expression(focused)
        if value is not None:
            return jsonify({"output": format_number(value)})

        # Fallback direct arithmetic on full query
        value = compute_binary_expression(query)
        if value is not None:
            return jsonify({"output": format_number(value)})

        return jsonify({"output": "0"})

    except Exception:
        return jsonify({"output": "0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
