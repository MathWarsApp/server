import random


class ExpressionGenerator:

    @staticmethod
    def generate_expression_level_1():
        operators1 = ['+', '-', '*']
        operators2 = ['+', '-', '*', '/']

        x = random.randint(1, 10)
        y = random.randint(1, 10)
        z = random.randint(1, 10)

        operator1 = random.choice(operators1)
        operator2 = random.choice(operators2)
        expression = f"{x} {operator1} {y} {operator2} {z}"

        return expression
