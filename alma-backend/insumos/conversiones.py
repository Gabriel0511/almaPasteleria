from decimal import Decimal

CONVERSIONES = {
    # --- PESO ---
    'kg': {'g': 1000, 'mg': 1000000},
    'g': {'kg': Decimal('0.001'), 'mg': 1000},
    'mg': {'kg': Decimal('0.000001'), 'g': Decimal('0.001')},

    # --- VOLUMEN ---
    'l': {'ml': 1000, 'cl': 100, 'cda': Decimal('66.6667'), 'cdta': Decimal('200')},
    'ml': {'l': Decimal('0.001'), 'cl': 0.1, 'cda': Decimal('0.0667'), 'cdta': Decimal('0.2')},
    'cl': {'l': Decimal('0.01'), 'ml': 10, 'cda': Decimal('0.667'), 'cdta': 2},
    'cda': {'ml': 15, 'l': Decimal('0.015'), 'cdta': 3},
    'cdta': {'ml': 5, 'l': Decimal('0.005'), 'cda': Decimal('0.333')},

    # --- UNIDADES ---
    'unidad': {'docena': Decimal('0.083333')},  # 1 unidad = 1/12 docena
    'docena': {'unidad': 12}
}

def convertir_unidad(cantidad, unidad_origen, unidad_destino):
    """
    Convierte una cantidad entre unidades compatibles (peso, volumen o unidades).
    """
    if unidad_origen == unidad_destino:
        return cantidad

    try:
        unidad_origen = unidad_origen.lower()
        unidad_destino = unidad_destino.lower()

        factor = CONVERSIONES[unidad_origen][unidad_destino]
        return cantidad * Decimal(str(factor))
    except KeyError:
        raise ValueError(f"No existe conversión de {unidad_origen} a {unidad_destino}")
