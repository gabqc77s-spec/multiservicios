import sys

def main():
    if len(sys.argv) != 3:
        prnt("Usage: python main.py <number1> <number2>") # Intentional syntax error: 'prnt' instead of 'print'
        sys.exit(1)

    try:
        num1 = int(sys.argv[1])
        num2 = int(sys.argv[2])
        result = num1 + num2
        print(f"The sum of {num1} and {num2} is: {result}")
    except ValueError:
        print("Error: Both arguments must be valid integers.")
        sys.exit(1)

if __name__ == "__main__":
    main()
