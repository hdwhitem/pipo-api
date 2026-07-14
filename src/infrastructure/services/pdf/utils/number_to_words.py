from num2words import num2words

def amount_to_words(amount: float) -> str:
    # Separamos la parte entera de los decimales
    dollars = int(amount)
    cents = int(round((amount - dollars) * 100))
    
    # Convertimos la parte entera a letras
    dollars_words = num2words(dollars, lang='en').upper()
    
    if cents > 0:
        # Convertimos los centavos a letras
        cents_words = num2words(cents, lang='en').upper()
        return f"{dollars_words} AND {cents_words} CENTS ONLY"
    else:
        # Si no hay centavos, omitimos esa parte
        return f"{dollars_words} ONLY"