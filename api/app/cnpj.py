"""CNPJ validation: 14 digits and both check digits (RF-01).

Pure function: no network, no database. Runs before any external call.
"""

PESOS_PRIMEIRO = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
PESOS_SEGUNDO = [6, *PESOS_PRIMEIRO]


def _digito(numeros: list[int], pesos: list[int]) -> int:
    resto = sum(n * p for n, p in zip(numeros, pesos, strict=True)) % 11
    return 0 if resto < 2 else 11 - resto


def cnpj_valido(cnpj: str) -> bool:
    """True when cnpj has exactly 14 digits (no mask) and valid check digits."""
    if len(cnpj) != 14 or not cnpj.isascii() or not cnpj.isdigit():
        return False
    if len(set(cnpj)) == 1:  # 00000000000000, 11111111111111... pass the formula but are not real
        return False
    numeros = [int(c) for c in cnpj]
    primeiro = _digito(numeros[:12], PESOS_PRIMEIRO)
    segundo = _digito([*numeros[:12], primeiro], PESOS_SEGUNDO)
    return numeros[12:] == [primeiro, segundo]
