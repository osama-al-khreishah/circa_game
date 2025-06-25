# app/utils.py
import random
from typing import Tuple

OPERATORS = ["+", "-", "*", "/"]

def generate_question(difficulty: int) -> Tuple[str, float]:
    operand_counts = {1: 2, 2: 3, 3: 4, 4: 5}
    digit_sizes = {1: 1, 2: 2, 3: 3, 4: 4}

    num_operands = operand_counts[difficulty]
    digit_length = digit_sizes[difficulty]

    operands = [
        str(random.randint(10**(digit_length - 1), 10**digit_length - 1))
        for _ in range(num_operands)
    ]

    operators = [random.choice(OPERATORS) for _ in range(num_operands - 1)]

    # Ensure no division by zero
    question = ""
    for i in range(num_operands - 1):
        question += operands[i] + " " + operators[i] + " "
    question += operands[-1]

    try:
        answer = round(eval(question), 2)
    except ZeroDivisionError:
        return generate_question(difficulty)

    return question, answer
