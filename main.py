from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def solve_query(query):
    q = query.lower()

    # Level 7 - Rule based logic
    if "apply rules" in q or "rule 1" in q:
        # Extract input number
        match = re.search(r"input number\s*(-?\d+)", q)
        if not match:
            return "0"
        n = int(match.group(1))

        # Rule 1: even -> double, odd -> add 10
        if n % 2 == 0:
            n = n * 2
        else:
            n = n + 10

        # Rule 2: > 20 -> subtract 5, else add 3
        if n > 20:
            n = n - 5
        else:
            n = n + 3

        # Rule 3: divisible by 3 -> FIZZ, else number
        if n % 3 == 0:
            return "FIZZ"
        else:
            return str(n)

    # Addition
    if any(w in q for w in ["plus", "add", "sum", "+"]):
        nums = re.findall(r"-?\d+", q)
        if len(nums) >= 2:
            return str(int(nums[0]) + int(nums[1]))

    # Subtraction
    if any(w in q for w in ["minus", "subtract", "difference", "-"]):
        nums = re.findall(r"-?\d+", q)
        if len(nums) >= 2:
            return str(int(nums[0]) - int(nums[1]))

    # Multiplication
    if any(w in q for w in ["times", "multiply", "multiplied", "product", "*", "x"]):
        nums = re.findall(r"-?\d+", q)
        if len(nums) >= 2:
            return str(int(nums[0]) * int(nums[1]))

    # Division
    if any(w in q for w in ["divide", "divided", "quotient", "/"]):
        nums = re.findall(r"-?\d+", q)
        if len(nums) >= 2 and int(nums[1]) != 0:
            return str(int(nums[0]) // int(nums[1]))

    # Fallback
    nums = re.findall(r"-?\d+", q)
    if len(nums) >= 2:
        return str(int(nums[0]) + int(nums[1]))

    return "0"

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    result = solve_query(query)
    return jsonify({"output": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
