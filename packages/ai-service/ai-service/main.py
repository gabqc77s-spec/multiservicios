from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        num1 = data.get('num1')
        num2 = data.get('num2')
        operation = data.get('operation', 'add') # Default to add

        if num1 is None or num2 is None:
            return jsonify({"error": "Missing num1 or num2"}), 400

        num1 = float(num1)
        num2 = float(num2)

        result = None
        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                return jsonify({"error": "Cannot divide by zero"}), 400
            result = num1 / num2
        else:
            return jsonify({"error": "Unsupported operation"}), 400

        return jsonify({"num1": num1, "num2": num2, "operation": operation, "result": result})
    except ValueError:
        return jsonify({"error": "Invalid number format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)