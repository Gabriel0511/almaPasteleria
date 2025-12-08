from decimal import Decimal

CONVERSIONES = {
    # --- PESO ---
    'kg': {'g': 1000, 'cda': Decimal('58.8235'), 'cdta': 200},
    'g': {'kg': Decimal('0.001'), 'cda': Decimal('0.0588'), 'cdta': Decimal('0.2')},

    # --- VOLUMEN ---
    'l': {'ml': 1000, 'cda': Decimal('66.6667'), 'cdta': Decimal('200')},
    'ml': {'l': Decimal('0.001'), 'cda': Decimal('0.0667'), 'cdta': Decimal('0.2')},
    'cda': {
        'ml': 15, 
        'l': Decimal('0.015'), 
        'cdta': 3,
        'g': 17,
        'kg': Decimal('0.017')
    },
    'cdta': {
        'ml': 5, 
        'l': Decimal('0.005'), 
        'cda': Decimal('0.333'),
        'g': 5,
        'kg': Decimal('0.005')
    },

    # --- UNIDADES ---
    'unidad': {'docena': Decimal('0.083333')},
    'docena': {'unidad': 12}
}

def convertir_unidad(cantidad, unidad_origen, unidad_destino):
    """
    Convierte una cantidad entre unidades compatibles.
    Devuelve float para compatibilidad con operaciones matemáticas.
    """
    if unidad_origen == unidad_destino:
        return float(cantidad)  # 🔹 Devuelve float

    try:
        unidad_origen = unidad_origen.lower()
        unidad_destino = unidad_destino.lower()

        factor = CONVERSIONES[unidad_origen][unidad_destino]
        # 🔹 CAMBIO IMPORTANTE: Convertir resultado a float
        resultado = float(Decimal(str(cantidad)) * Decimal(str(factor)))
        return resultado
        
    except KeyError:
        # Si no hay conversión directa, buscar ruta indirecta
        try:
            # Para cucharada/cucharadita entre peso y volumen
            if unidad_origen in ['kg', 'g'] and unidad_destino in ['cda', 'cdta']:
                # Convertir primero a gramos si es necesario
                if unidad_origen == 'kg':
                    cantidad_g = Decimal(str(cantidad)) * 1000
                else:
                    cantidad_g = Decimal(str(cantidad))
                
                # Luego a cucharada/cucharadita
                if unidad_destino == 'cda':
                    resultado = float(cantidad_g / Decimal('17'))
                else:  # cdta
                    resultado = float(cantidad_g / Decimal('5'))
                return resultado
            
            elif unidad_origen in ['cda', 'cdta'] and unidad_destino in ['kg', 'g']:
                # Convertir primero a gramos
                if unidad_origen == 'cda':
                    cantidad_g = Decimal(str(cantidad)) * Decimal('17')
                else:  # cdta
                    cantidad_g = Decimal(str(cantidad)) * Decimal('5')
                
                # Luego a kg o g
                if unidad_destino == 'kg':
                    resultado = float(cantidad_g / 1000)
                else:  # g
                    resultado = float(cantidad_g)
                return resultado
            
            else:
                # Si no hay conversión, devolver cantidad original como float
                return float(cantidad)
                
        except Exception as e:
            print(f"⚠️ Error en conversión indirecta: {e}")
            return float(cantidad)  # Fallback: devolver cantidad original como float