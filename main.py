import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = text.replace("×", "*").replace("·", "*").replace("÷", "/")
    text = text.replace("^", "^")
    text = re.sub(r"\s+", " ", text)
    return text

def parse_int(s: str) -> int:
    return int(s.replace(",", ""))

def solve_modexp(q: str):
    """
    Handles:
    - What are the last 6 digits of 7^777?
    - compute 7^777 mod 10^6
    - 7^777 modulo 10^6
    """
    qn = normalize(q)

    # Pattern 1: "last N digits of A^B"
    m = re.search(r"last\s+(\d+)\s+digits?\s+of\s+([+-]?\d+)\s*\^\s*([+-]?\d+)", qn)
    if m:
        digits = parse_int(m.group(1))
        base = parse_int(m.group(2))
        exp = parse_int(m.group(3))
        mod = 10 ** digits
        return str(pow(base, exp, mod))

    # Pattern 2: "A^B mod 10^N"
    m = re.search(
        r"([+-]?\d+)\s*\^\s*([+-]?\d+)\s*(?:mod|ulo|modulo|%?)\s*10\s*\^\s*(\d+)",
        qn
    )
    if m:
        base = parse_int(m.group(1))
        exp = parse_int(m.group(2))
        digits = parse_int(m.group(3))
        mod = 10 ** digits
        return str(pow(base, exp, mod))

    # Pattern 3: "compute A^B mod 1000000"
    m = re.search(r"([+-]?\d+)\s*\^\s*([+-]?\d+)\s*(?:mod|ulo|modulo)\s*([+-]?\d+)", qn)
    if m:
        base = parse_int(m.group(1))
        exp = parse_int(m.group(2))
        mod = abs(parse_int(m.group(3)))
        if mod == 0:
            return "0"
        return str(pow(base, exp, mod))

    return None

def solve_basic_arithmetic(q: str):
    """
    Small fallback for simple arithmetic queries.
    Supports plus, minus, times, divided by.
    """
    qn = normalize(q)

    # Replace words with operators
    qn = re.sub(r"\bdivided by\b", "/", qn)
    qn = re.sub(r"\bover\b", "/", qn)
    qn = re.sub(r"\btimes\b", "*", qn)
    qn = re.sub(r"\bmultiplied by\b", "*", qn)
    qn = re.sub(r"\bplus\b", "+", qn)
    qn = re.sub(r"\bminus\b", "-", qn)

    nums = re.findall(r"[+-]?\d+(?:\.\d+)?", qn)
    if not nums:
        return None

    try:
        values = [float(x) for x in nums]

        if "/" in qn:
            result = values[0]
            for v in values[1:]:
                if v == 0:
                    return "0"
                result /= v
        elif "*" in qn:
            result = 1
            for v in values:
                result *= v
        elif "-" in qn:
            result = values[0]
            for v in values[1:]:
                result -= v
        else:
            result = sum(values)

        if abs(result - round(result)) < 1e-12:
            return str(int(round(result)))
        return str(result)
    except Exception:
        return None

@app.route("/v1/answer", methods=["POST"])
def answer():
    try:
        data = request.get_json(silent=True) or {}
        query = data.get("query", "")

        result = solve_modexp(query)
        if result is None:
            result = solve_basic_arithmetic(query)

        if result is None:
            result = "0"

        return jsonify({"output": result})
    except Exception:
        return jsonify({"output": "0"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
