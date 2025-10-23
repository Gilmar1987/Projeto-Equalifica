import re
from django.core.exceptions import ValidationError

def validate_cpf(value):
    """
    Validates a Brazilian CPF number.
    A CPF is composed of 11 digits, often formatted as XXX.XXX.XXX-XX.
    This function checks the format and the validity of the CPF number.
    """
    cpf_pattern = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$')
    
    if not cpf_pattern.match(value):
        raise ValidationError('Invalid CPF format. Expected XXX.XXX.XXX-XX or XXXXXXXXXXX.')

    # Remove formatting characters
    cpf_numbers = re.sub(r'\D', '', value)

    if len(cpf_numbers) != 11 or cpf_numbers == cpf_numbers[0] * 11:
        raise ValidationError('Invalid CPF number.')

    def calculate_digit(digits):
        sum_ = sum(int(digit) * weight for digit, weight in zip(digits, range(len(digits) + 1, 1, -1)))
        remainder = sum_ % 11
        return '0' if remainder < 2 else str(11 - remainder)

    first_digit = calculate_digit(cpf_numbers[:9])
    second_digit = calculate_digit(cpf_numbers[:10])

    if cpf_numbers[-2:] != first_digit + second_digit:
        raise ValidationError('Invalid CPF number.')
    
def validate_cnpj(value):
    """
    Validates a Brazilian CNPJ number.
    A CNPJ is composed of 14 digits, often formatted as XX.XXX.XXX/0001-XX.
    This function checks the format and the validity of the CNPJ number.
    """
    cnpj_pattern = re.compile(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$')
    
    if not cnpj_pattern.match(value):
        raise ValidationError('Invalid CNPJ format. Expected XX.XXX.XXX/0001-XX or XXXXXXXXXXXXXX.')

    # Remove formatting characters
    cnpj_numbers = re.sub(r'\D', '', value)

    if len(cnpj_numbers) != 14 or cnpj_numbers == cnpj_numbers[0] * 14:
        raise ValidationError('Invalid CNPJ number.')

    def calculate_digit(digits, weights):
        sum_ = sum(int(digit) * weight for digit, weight in zip(digits, weights))
        remainder = sum_ % 11
        return '0' if remainder < 2 else str(11 - remainder)

    first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_weights = [6] + first_weights

    first_digit = calculate_digit(cnpj_numbers[:12], first_weights)
    second_digit = calculate_digit(cnpj_numbers[:13], second_weights)

    if cnpj_numbers[-2:] != first_digit + second_digit:
        raise ValidationError('Invalid CNPJ number.')