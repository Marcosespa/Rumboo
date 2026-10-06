import re


def normalize_plate(value):
    value = re.sub(r"[\s-]", "", value).upper()
    if not re.fullmatch(r"[A-Z]{3}\d{3}", value):
        raise ValueError("La placa debe tener tres letras y tres números")
    return value


def normalize_phone(value):
    value = re.sub(r"[\s()-]", "", value)
    if value.startswith("+57"):
        value = value[3:]
    if not re.fullmatch(r"3\d{9}", value):
        raise ValueError("Ingresa un celular colombiano de diez dígitos que empiece por 3")
    return "+57" + value
