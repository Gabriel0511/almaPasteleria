# conversiones.py
from decimal import Decimal

CONVERSIONES = {
    'kg': {
        'g': Decimal('1000'),
        'mg': Decimal('1000000')
    },
    'g': {
        'kg': Decimal('0.001'),
        'mg': Decimal('1000')
    },
    'l': {
        'ml': Decimal('1000'),
        'cl': Decimal('100')
    },
    'ml': {
        'l': Decimal('0.001'),
        'cl': Decimal('0.1')
    },
    'unidades': {
        'docena': Decimal('12'),
        'media_docena': Decimal('6')
    }
}

def convertir_unidad(valor, unidad_origen, unidad_destino):
    """
    Convierte un valor de una unidad a otra
    """
    if unidad_origen == unidad_destino:
        return valor
    
    if unidad_origen in CONVERSIONES and unidad_destino in CONVERSIONES[unidad_origen]:
        factor = CONVERSIONES[unidad_origen][unidad_destino]
        return valor * factor
    
    # Si no hay conversión directa, intenta la inversa
    if unidad_destino in CONVERSIONES and unidad_origen in CONVERSIONES[unidad_destino]:
        factor = CONVERSIONES[unidad_destino][unidad_origen]
        return valor / factor
    
    raise ValueError(f"No se puede convertir de {unidad_origen} a {unidad_destino}")