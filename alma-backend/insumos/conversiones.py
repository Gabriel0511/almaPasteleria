# conversiones.py
from decimal import Decimal


CONVERSIONES = {
    'kg': {'g': 1000, 'mg': 1000000},
    'g': {'kg': 0.001, 'mg': 1000},
    'mg': {'kg': 0.000001, 'g': 0.001},
    'l': {'ml': 1000, 'cl': 100},
    'ml': {'l': 0.001, 'cl': 0.1},
    'cl': {'l': 0.01, 'ml': 10},
}

def convertir_unidad(cantidad, unidad_origen, unidad_destino):
    if unidad_origen == unidad_destino:
        return cantidad
    
    try:
        factor = CONVERSIONES[unidad_origen][unidad_destino]
        return cantidad * Decimal(str(factor))
    except KeyError:
        raise ValueError(f"No existe conversión de {unidad_origen} a {unidad_destino}")