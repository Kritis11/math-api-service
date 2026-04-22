from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# ============ ROUTER FUNCTION ============
def route_and_process(query):
    """
    Main router that decides: Level 1 (Math) or Level 2 (Date Extraction)
    """
    query_lower = query.lower()
    
    # Check for Level 2 keywords
    if "extract" in query_lower or "date" in query_lower:
        return handle_date_extraction(query)
    
    # Default to Level 1
    else:
        return handle_math(query)


# ============ LEVEL 2: DATE EXTRACTION ============
def handle_date_extraction(query):
    """
    Extract date in format: "Day Month Year"
    Example: "12 March 2024"
    """
    # Pattern matches: 1-2 digits + space + letters + space + 4 digits
    date_pattern = r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})"
    match = re.search(date_pattern, query)
    
    if match:
        return match.group(1)
    else:
        return "Date not found"


# ============ LEVEL 1: MATH ============
def handle_math(query):
    """
    Extract numbers and perform arithmetic
    Returns: "The sum is X."
    """
    query_lower = query.lower()
    
    # Extract all numbers (including negatives)
    numbers = re.findall(r"-?\d+", query)
    
    if len(numbers) < 2:
        return "The sum is 0."
    
    nums = [int(n) for n in numbers]
    result = 0
    
    # Determine operation
    if "plus" in query_lower or "+" in query_lower or "add" in query_lower:
        result = nums[0] + nums[1]
    elif "minus" in query_lower or "-" in query_lower or "subtract" in query_lower:
        result = nums[0] - nums[1]
    elif "times" in query_lower or "*" in query_lower or "multiply" in query_lower or "x" in query_lower:
        result = nums[0] * nums[1]
    elif "divide" in query_lower or "/" in query_lower:
        if nums[1] != 0:
            result = nums[0] // nums[1]
        else:
            result = 0
    else:
        result = sum(nums)
    
    return f"The sum is {result}."


# ============ API ENDPOINT ============
@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.get_json()
    query = data.get("query", "")
    
    # Route and process the query
    output = route_and_process(query)
    
    return jsonify({"output": output})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
