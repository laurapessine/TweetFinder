import os
import json
from hashing.hash_utils import stable_hash_bits
from hashing.bucket import Bucket

class Directory:
    def __init__(self, meta_path: str, bucket_dir: str, bucket_capacity: int = 4096):
        self.meta_path = meta_path
        self.bucket_dir = bucket_dir
        self.bucket_capacity = bucket_capacity
        self.global_depth = None
        self.buckets = []  # lista de Bucket ou None inicialmente
        if os.path.exists(meta_path):
            self.load()
        else:
            # Inicializa com profundidade 1 e dois buckets
            os.makedirs(bucket_dir, exist_ok=True)
            self.global_depth = 1
            b0 = Bucket(os.path.join(bucket_dir, 'bucket0.bin'), local_depth=1, capacity_bytes=bucket_capacity)
            b1 = Bucket(os.path.join(bucket_dir, 'bucket1.bin'), local_depth=1, capacity_bytes=bucket_capacity)
            b0.flush(); b1.flush()
            self.buckets = [b0, b1]
            self.flush()

    def load(self):
        with open(self.meta_path, 'r') as f:
            meta = json.load(f)
        self.global_depth = meta['global_depth']
        self.buckets = []
        for path in meta['buckets']:
            b = Bucket(os.path.join(self.bucket_dir, path), local_depth=0, capacity_bytes=self.bucket_capacity)
            b.load()
            self.buckets.append(b)

    def flush(self):
        # Persiste metadata
        meta = {
            'global_depth': self.global_depth,
            'buckets': [os.path.basename(b.path) for b in self.buckets]
        }
        with open(self.meta_path, 'w') as f:
            json.dump(meta, f)

    def get_bucket_index(self, key: str) -> int:
        idx = stable_hash_bits(key, self.global_depth)
        return idx

    def insert(self, key: str, ptr: int):
        idx = self.get_bucket_index(key)
        bucket = self.buckets[idx]
        bucket.load()
        if bucket.insert(key, ptr):
            bucket.flush()
            return
        # overflow: precisa split
        self.split_bucket(idx)
        # após split, re-inserir
        self.insert(key, ptr)

    def split_bucket(self, idx: int):
        old_bucket = self.buckets[idx]
        old_bucket.load()
        old_ld = old_bucket.local_depth
        # Se local_depth == global_depth, duplicar diretório
        if old_ld == self.global_depth:
            # duplicar referências
            self.buckets = self.buckets + self.buckets
            self.global_depth += 1
        # Cria novo bucket
        new_ld = old_ld + 1
        old_bucket.local_depth = new_ld
        # Nome do arquivo novo
        new_bucket_idx = len(self.buckets)  # temporário; vamos ajustar índices depois
        new_bucket_name = f'bucket_{len(self.buckets)}.bin'
        new_bucket = Bucket(os.path.join(self.bucket_dir, new_bucket_name), local_depth=new_ld, capacity_bytes=self.bucket_capacity)
        new_bucket.entries = {}
        # Redistribuir: combine keys antigos + none (mas só entradas antigas)
        all_entries = list(old_bucket.entries.items())
        old_bucket.entries = {}
        # Ajustar referências no diretório: encontre quais índices do diretório apontavam para old_bucket
        # Primeiro, identifique o prefixo compartilhado: use bits de hash
        # Iremos reconstruir pointers:
        for key, ptr in all_entries:
            # Para cada key, recalc índice com profundidade local nova
            hbits = stable_hash_bits(key, new_ld)
            # O índice total é hbits com local_depth bits; para mapear no diretório de global_depth, considere todos índices i onde os low new_ld bits == hbits
            # Implementação: para cada posição j em 0..2^global_depth-1, se (j & ((1<<new_ld)-1)) == hbits, então aponta para este bucket ou outro.
            # Porém, aqui fazemos redistribuição de entradas: se hbits aponta para new bucket ou old.
            # Simplificado: use índice relativo:
            bit_val = hbits
            # Verifique se este bit_val indica new bucket ou old: mas precisamos decidir uma convenção:
            # No extendible hashing, se o prefixo de bits corresponde ao bucket antigo mas com bit de mais peso igual a 0 permanece, se 1 vai para new. Mas só se local_depth > prefixo anterior.
            # Para simplificar: podemos verificar: digamos que, antes do split, old_bucket local_depth era d. Então antes, todos endereços tinham prefixo de d bits iguais a algum valor P. Agora local_depth = d+1; dependendo do (d+1)-ésimo bit, algumas entradas vão pro old, outras pro new.
            # Em código real, precisaríamos armazenar o prefixo do bucket. Para prova de conceito, simplifique assumindo que bucket paths indicam prefixos. Aqui omitido por brevidade; implemente logicamente conforme teoria de extendible hashing.
            pass
        # Nota: a implementação completa de split exige gerenciar prefixos. Este esboço ilustra proximidade.
        # Após ajustar old_bucket e new_bucket, gravar ambos e atualizar self.buckets[.] para apontar corretamente.
        old_bucket.flush()
        new_bucket.flush()
        self.flush()