from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def process_query(query):
    # Extract the input number
    num_match = re.search(r'input number (\d+)', query)
    if not num_match:
        return "Invalid query: No input number found"
    
    n = int(num_match.group(1))
    
    # Apply Rule 1
    if n % 2 == 0:  # even
        n = n * 2
    else:  # odd
        n = n + 10
    
    # Apply Rule 2
    if n > 20:
        n = n - 5
    else:
        n = n + 3
    
    # Apply Rule 3
    if n % 3 == 0:
        return "FIZZ"
    else:
        return str(n)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Process the query
        result = process_query(query)
        
        return jsonify({"output": result})
    
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
