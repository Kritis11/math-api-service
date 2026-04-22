from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def solve_rules(q):
    # Extract starting number
    start = int(re.search(r"number\s*(-?\d+)", q).group(1))
    res = start

    # --- Rule 1 ---
    if res % 2 == 0:
        # even branch
        if "double it" in q:
            res *= 2
        elif "triple it" in q:
            res *= 3
        elif "multiply by" in q:
            m = re.search(r"multiply by (\d+)", q)
            if m: res *= int(m.group(1))
        elif "add" in q:
            m = re.search(r"even\s*→\s*add\s*(\d+)", q)
            if m: res += int(m.group(1))
    else:
        # odd branch
        if "double it" in q:
            res *= 2
        elif "triple it" in q:
            res *= 3
        elif "multiply by" in q:
            m = re.search(r"multiply by (\d+)", q)
            if m: res *= int(m.group(1))
        elif "add" in q:
            m = re.search(r"odd\s*→\s*add\s*(\d+)", q)
            if m: res += int(m.group(1))

    # --- Rule 2 ---
    comp = re.search(r"result\s*>\s*(\d+)", q)
    if comp:
        threshold = int(comp.group(1))
        if res > threshold:
            m = re.search(r"subtract\s*(\d+)", q)
            if m: res -= int(m.group(1))
            m = re.search(r"divide by (\d+)", q)
            if m: res //= int(m.group(1))
        else:
            m = re.search(r"Otherwise\s*→\s*add\s*(\d+)", q)
            if m: res += int(m.group(1))
            m = re.search(r"Otherwise\s*→\s*multiply by (\d+)", q)
            if m: res *= int(m.group(1))

    # --- Rule 3 ---
    div = re.search(r"divisible\s*by\s*(\d+)", q)
    word = re.search(r"output\s*\"([^\"]+)\"", q)
    if div and word:
        divisor = int(div.group(1))
        label = word.group(1)
        if res % divisor == 0:
            return label

    return str(res)

def solve_math(q):
    nums = re.findall(r"-?\d+", q)
    if not nums:
        return "0"
    nums = [int(n) for n in nums]
    q = q.lower()

    if any(op in q for op in ["plus", "add", "sum", "+"]):
        return str(sum(nums))
    if any(op in q for op in ["minus", "subtract", "-"]):
        return str(nums[0] - nums[1] if len(nums) >= 2 else nums[0])
    if any(op in q for op in ["times", "multiply", "multiplied", "*"]):
        return str(nums[0] * nums[1] if len(nums) >= 2 else nums[0])
    if any(op in q for op in ["divided", "divide", "/"]):
        return str(nums[0] // nums[1] if len(nums) >= 2 else nums[0])

    return str(nums[0])

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")

    if not query:
        return jsonify({"output": "0"})

    # Detect rule-based queries
    if "Rule" in query or "rules" in query.lower():
        result = solve_rules(query)
        return jsonify({"output": result})
    else:
        val = solve_math(query)
        return jsonify({"output": f"The sum is {val}."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
