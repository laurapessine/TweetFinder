import struct

class PostingListReader:
    def __init__(self, path: str, id_size_bytes: int = 4, buffer_size_bytes: int = 4096):
        self.path = path
        self.id_size = id_size_bytes
        self.buffer_size = buffer_size_bytes
        self.file = open(path, 'rb')
        # Se houver cabeçalho (e.g., número de itens), leia aqui; ou ignore se não necessário.
        self.buffer = b''
        self.offset = 0  # deslocamento dentro do buffer
        self.eof = False
        self.next_id = None
        self._fill_buffer()
        self._load_next()

    def _fill_buffer(self):
        # Move dados restantes para início e completa buffer
        data = self.buffer[self.offset:]
        new = self.file.read(self.buffer_size)
        self.buffer = data + new
        self.offset = 0
        if not new and not data:
            self.eof = True

    def _load_next(self):
        # Tenta carregar próximo ID em self.next_id; se buffer exaurido, tenta refil
        while True:
            if self.eof and self.offset >= len(self.buffer):
                self.next_id = None
                return
            # Verifica se há bytes suficientes para um ID
            if len(self.buffer) - self.offset < self.id_size:
                if self.eof:
                    # Não há mais dados
                    self.next_id = None
                    return
                # tenta refil
                self._fill_buffer()
                continue
            # Ler bytes do ID
            raw = self.buffer[self.offset:self.offset + self.id_size]
            # Supondo formato big-endian unsigned int: '>I'; ajuste se quiser little-endian
            self.next_id = struct.unpack('>I', raw)[0]
            self.offset += self.id_size
            return

    def peek(self):
        return self.next_id

    def next(self):
        current = self.next_id
        if current is None:
            return None
        self._load_next()
        return current

    def close(self):
        self.file.close()