import hashlib

def stable_hash_bits(key: str, bits: int) -> int:
    # Usa SHA-1 e retorna os bits menos significativos
    h = int(hashlib.sha1(key.encode('utf-8')).hexdigest(), 16)
    return h & ((1 << bits) - 1)