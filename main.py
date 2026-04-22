from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    try:
        data = request.get_json()
        query = data.get('query', '')
        # Extract all numbers and sum them
        numbers = re.findall(r'-?\d+', query)
        result = sum(int(num) for num in numbers)
        return jsonify({"output": f"The sum is {result}."})
    except:
        return jsonify({"output": "The sum is 0."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
