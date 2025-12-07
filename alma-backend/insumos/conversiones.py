from decimal import Decimal

CONVERSIONES = {
    # --- PESO ---
    'kg': {'g': 1000, 'cda': Decimal('58.8235'), 'cdta': 200},  # 1kg = 1000g = ~58.8 cda (17g/cda) = 200 cdta (5g/cdta)
    'g': {'kg': Decimal('0.001'), 'cda': Decimal('0.0588'), 'cdta': Decimal('0.2')},  # 1g = 0.001kg = ~0.0588 cda = 0.2 cdta

    # --- VOLUMEN ---
    'l': {'ml': 1000, 'cda': Decimal('66.6667'), 'cdta': Decimal('200')},
    'ml': {'l': Decimal('0.001'), 'cda': Decimal('0.0667'), 'cdta': Decimal('0.2')},
    'cda': {
        'ml': 15, 
        'l': Decimal('0.015'), 
        'cdta': 3,
        'g': 17,  # Para conversiones de volumen a peso
        'kg': Decimal('0.017')
    },
    'cdta': {
        'ml': 5, 
        'l': Decimal('0.005'), 
        'cda': Decimal('0.333'),
        'g': 5,  # Para conversiones de volumen a peso
        'kg': Decimal('0.005')
    },

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
        # Si no hay conversión directa, buscar ruta indirecta
        try:
            # Para cucharada/cucharadita entre peso y volumen
            if unidad_origen in ['kg', 'g'] and unidad_destino in ['cda', 'cdta']:
                # Convertir primero a gramos si es necesario
                if unidad_origen == 'kg':
                    cantidad_g = cantidad * 1000
                else:
                    cantidad_g = cantidad
                
                # Luego a cucharada/cucharadita
                if unidad_destino == 'cda':
                    return cantidad_g / Decimal('17')
                else:  # cdta
                    return cantidad_g / Decimal('5')
            
            elif unidad_origen in ['cda', 'cdta'] and unidad_destino in ['kg', 'g']:
                # Convertir primero a gramos
                if unidad_origen == 'cda':
                    cantidad_g = cantidad * Decimal('17')
                else:  # cdta
                    cantidad_g = cantidad * Decimal('5')
                
                # Luego a kg o g
                if unidad_destino == 'kg':
                    return cantidad_g / 1000
                else:  # g
                    return cantidad_g
            
            else:
                raise ValueError(f"No existe conversión de {unidad_origen} a {unidad_destino}")
                
        except:
            raise ValueError(f"No existe conversión de {unidad_origen} a {unidad_destino}")