from num2words import num2words

def amount_to_words(amount: float, currency_symbol: str = "USD") -> str:
    # Divide parte entera y decimal para formato bancario
    dollars = int(amount)
    cents = int(round((amount - dollars) * 100))
    
    words = num2words(dollars, lang='en').upper()
    return f"{words} {currency_symbol} AND {cents}/100 CENTS ONLY"