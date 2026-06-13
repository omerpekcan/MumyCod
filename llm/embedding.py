import math

def get_embedding(text: str) -> list[float]:
    """
    Metni yerel ve deterministik bir şekilde 128 boyutlu bir vektöre dönüştürür.
    Herhangi bir API çağrısı yapmaz, tamamen yerel çalışır.
    """
    vector_size = 128
    vector = [0.0] * vector_size
    
    if not text:
        return vector

    # Metni karakter bazlı özellik vektörüne dönüştür (Feature Hashing)
    for i, char in enumerate(text):
        # Karakterin ASCII değerini ve pozisyonunu kullanarak deterministik bir indeks oluştur
        char_val = ord(char)
        idx = (char_val + i * 31) % vector_size
        
        # Vektörü güncelle
        vector[idx] += 1.0
    
    # Vektörü normalize et (L2 Norm)
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [x / norm for x in vector]
    
    return vector
