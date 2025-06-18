import struct
import os

class Bucket:
    def __init__(self, path: str, local_depth: int, capacity_bytes: int = 4096):
        self.path = path
        self.local_depth = local_depth
        self.entries = {}  # em memória: key -> pointer (int ou string)
        self.capacity_bytes = capacity_bytes

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, 'rb') as f:
            # Exemplo de formato: local_depth (1 byte), num_entries (4 bytes)
            header = f.read(5)
            if not header:
                return
            ld, num = struct.unpack('>BI', header)
            self.local_depth = ld
            self.entries = {}
            for _ in range(num):
                key_len_bytes = f.read(2)
                klen = struct.unpack('>H', key_len_bytes)[0]
                key = f.read(klen).decode('utf-8')
                # Supondo ponteiro 8 bytes (offset)
                ptr = struct.unpack('>Q', f.read(8))[0]
                self.entries[key] = ptr

    def flush(self):
        # Serializa entries. Se exceder capacity_bytes, sinalizar overflow externamente
        # Para simplificar, aqui não checamos tamanho; a lógica externa verifica antes de flush.
        with open(self.path, 'wb') as f:
            f.write(struct.pack('>BI', self.local_depth, len(self.entries)))
            for key, ptr in self.entries.items():
                key_b = key.encode('utf-8')
                f.write(struct.pack('>H', len(key_b)))
                f.write(key_b)
                f.write(struct.pack('>Q', ptr))

    def can_insert(self, key: str) -> bool:
        # Estima tamanho se inserisse: cabe nos capacity_bytes?
        # Simplificação: calcula tamanho serializado
        current = 5  # header
        for k, _ in self.entries.items():
            current += 2 + len(k.encode('utf-8')) + 8
        if key in self.entries:
            return True  # apenas atualização
        needed = 2 + len(key.encode('utf-8')) + 8
        return (current + needed) <= self.capacity_bytes

    def insert(self, key: str, ptr: int) -> bool:
        # Retorna True se inserido sem overflow; False se overflow ocorreria
        if key in self.entries:
            self.entries[key] = ptr
            return True
        if self.can_insert(key):
            self.entries[key] = ptr
            return True
        else:
            return False

    def find(self, key: str):
        return self.entries.get(key)