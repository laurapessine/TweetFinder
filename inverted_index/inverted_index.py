class InvertedIndex:
    def __init__(self, docs):
        #dicionário para o índice invertido
        self.invIndex = {}
        self.root = docs
        #processa os documentos (tweets)
        for i, t in enumerate(docs):
            self.parse(i,t)
    def parse(self, idoc, tokens):
        #percorre os tokens do documento
        for token in tokens:
            if token in self.invIndex:
                # adiciona apenas se ainda não estiver na lista
                if idoc not in self.invIndex[token]:
                    self.invIndex[token].append(idoc)
            else:
                self.invIndex[token] = [idoc]
    
    def search(self, word):
        if word in self.invIndex:
            return self.invIndex[word][:]
        else:
            return []
        
titles_tokens = [
    ["human", "machine", "interface", "for", "abc", "computer", "applications"],
    ["a", "survey", "of", "user", "opinion", "of", "computer", "system", "responde", "time"],
    ["the", "eps", "user", "interface", "management", "system"],
    ["system", "and", "human", "system", "engineering", "testing", "of", "eps"],
    ["relation", "of", "user", "perceived", "response", "time", "to", "error", "measurement"],
    ["the", "generation", "of", "random", "binary", "ordered", "trees"],
    ["the", "intersection", "graph", "of", "paths", "in", "trees"],
    ["graph", "minors", "iv", "widths", "of", "trees", "and", "well", "quasi", "ordering"],
    ["graph", "minors", "a", "survey"]
]

#cria o índice
index = InvertedIndex(titles_tokens)

#busca os termos
results = index.search('graph')

#impressão do resultado
for r in results:
    print(f"Doc({r}) =", " ".join(titles_tokens[r]))