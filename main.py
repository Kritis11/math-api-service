from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def solve_dynamic_rules(q):
    try:
        # 1. Extract the starting number (e.g., "number 6")
        start_num = int(re.search(r"number\s*(-?\d+)", q).group(1))
        
        # 2. Rule 1: If even -> operation, If odd -> operation
        # We look for words like "double", "triple", "add X", "multiply by X"
        res = start_num
        if res % 2 == 0:
            if "double it" in q: res *= 2
            elif "triple it" in q: res *= 3
            else:
                match = re.search(r"even\s*→\s*(?:add|plus)\s*(\d+)", q)
                if match: res += int(match.group(1))
        else:
            match = re.search(r"odd\s*→\s*(?:add|plus)\s*(\d+)", q)
            if match: res += int(match.group(1))

        # 3. Rule 2: If result > X -> operation. Otherwise -> operation.
        comp_match = re.search(r"result\s*>\s*(\d+)", q)
        if comp_match:
            threshold = int(comp_match.group(1))
            if res > threshold:
                sub_match = re.search(r"subtract\s*(\d+)", q)
                if sub_match: res -= int(sub_match.group(1))
            else:
                add_match = re.search(r"Otherwise\s*→\s*add\s*(\d+)", q)
                if add_match: res += int(add_match.group(1))

        # 4. Rule 3: If divisible by X -> output "WORD"
        div_match = re.search(r"divisible\s*by\s*(\d+)", q)
        word_match = re.search(r"output\s*\"([^\"]+)\"", q)
        if div_match and word_match:
            divisor = int(div_match.group(1))
            word = word_match.group(1)
            if res % divisor == 0:
                return word
        
        return str(res)
    except:
        return "Error"

def solve_math(q):
    nums = re.findall(r"-?\d+", q)
    if not nums: return "0"
    
    # Standard math logic
    nums = [int(n) for n in nums]
    if "plus" in q or "add" in q or "+" in q:
        return str(sum(nums))
    if "minus" in q or "subtract" in q or "-" in q:
        return str(nums[0] - nums[1])
    if "times" in q or "multipl" in q or "*" in q:
        return str(nums[0] * nums[1])
    return str(nums[0])

@app.route("/v1/answer", methods=["POST"])
def answer():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    
    if "Rule" in query or "rules" in query.lower():
        # For Level 7 rule queries, return the raw result (FIZZ or Number)
        result = solve_dynamic_rules(query)
        return jsonify({"output": result})
    else:
        # For standard math, use the STRICT FORMAT: "The sum is X."
        val = solve_math(query.lower())
        return jsonify({"output": f"The sum is {val}."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
