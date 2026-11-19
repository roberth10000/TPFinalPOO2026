from datetime import date, time, datetime


def parse_data(texto: str) -> date:
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Data inválida. Use dd/mm/aaaa.")


def parse_hora(texto: str) -> time:
    try:
        return datetime.strptime(texto.strip(), "%H:%M").time()
    except ValueError:
        raise ValueError("Horário inválido. Use HH:MM.")


def parse_float(texto: str) -> float:
    texto = texto.strip().replace(",", ".")
    if not texto:
        return 0.0
    try:
        return float(texto)
    except ValueError:
        raise ValueError("Valor numérico inválido.")