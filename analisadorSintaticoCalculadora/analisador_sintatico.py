class AnalisadorSintatico:
    def __init__(self):
        # Definição dos símbolos terminais e não-terminais
        self.terminais = ['id', 'int', 'float', 'char', ',', ';', '$']
        self.nao_terminais = ['P', 'DECL', 'TIPO', 'LISTA_ID', 'LISTA_ID_']
        
        # Tabela de análise preditiva
        self.tabela = {
            'P': {
                'int': ['TIPO', 'LISTA_ID', ';'],
                'float': ['TIPO', 'LISTA_ID', ';'],
                'char': ['TIPO', 'LISTA_ID', ';'],
                '$': ['ε']
            },
            'TIPO': {
                'int': ['int'],
                'float': ['float'],
                'char': ['char']
            },
            'LISTA_ID': {
                'id': ['id', 'LISTA_ID_']
            },
            'LISTA_ID_': {
                ',': [',', 'id', 'LISTA_ID_'],
                ';': ['ε']
            }
        }
    
    def tokenizar(self, entrada):
        # Função para tokenizar a entrada
        tokens = []
        entrada = entrada.strip()
        
        i = 0
        while i < len(entrada):
            if entrada[i].isspace():
                i += 1
                continue
            
            # Verifica palavras-chave ou identificadores
            if entrada[i].isalpha():
                start = i
                while i < len(entrada) and (entrada[i].isalnum() or entrada[i] == '_'):
                    i += 1
                palavra = entrada[start:i]
                
                if palavra in ['int', 'float', 'char']:
                    tokens.append(('TIPO', palavra))
                else:
                    tokens.append(('id', palavra))
            
            # Verifica símbolos
            elif entrada[i] == ',':
                tokens.append((',', ','))
                i += 1
            elif entrada[i] == ';':
                tokens.append((';', ';'))
                i += 1
            else:
                # Caractere inválido
                return None, f"Erro léxico: caractere inválido '{entrada[i]}' na posição {i}"
        
        tokens.append(('$', '$'))  # Marca o fim da entrada
        return tokens, None
    
    def analisar(self, tokens):
        pilha = ['$', 'P']  # Inicializa a pilha com o símbolo inicial e o marcador de fim
        entrada = tokens.copy()
        passos = []
        
        while pilha[-1] != '$':
            topo = pilha[-1]
            token_atual = entrada[0][0]  # Pegamos apenas o tipo do token
            
            # Registra o passo atual para debug
            passos.append({
                'pilha': pilha.copy(),
                'entrada': [t[0] for t in entrada],
                'acao': ''
            })
            
            # Se o topo da pilha é um terminal
            if topo in self.terminais:
                if topo == token_atual:
                    pilha.pop()
                    entrada.pop(0)
                    passos[-1]['acao'] = f"Consumir {topo}"
                else:
                    erro = f"Erro sintático: esperado '{topo}', encontrado '{token_atual}'"
                    passos[-1]['acao'] = f"ERRO: {erro}"
                    return False, erro, passos
            
            # Se o topo da pilha é epsilon
            elif topo == 'ε':
                pilha.pop()
                passos[-1]['acao'] = "Remover ε"
            
            # Se o topo da pilha é um não-terminal
            else:
                if topo in self.tabela and token_atual in self.tabela[topo]:
                    producao = self.tabela[topo][token_atual]
                    pilha.pop()
                    # Adiciona a produção na ordem inversa
                    for simbolo in reversed(producao):
                        if simbolo != 'ε':  # Não adiciona epsilon diretamente
                            pilha.append(simbolo)
                    passos[-1]['acao'] = f"Expandir {topo} -> {' '.join(producao)}"
                else:
                    erro = f"Erro sintático: não há produção para {topo} com entrada {token_atual}"
                    passos[-1]['acao'] = f"ERRO: {erro}"
                    return False, erro, passos
        
        # Verifica se ainda existe entrada não consumida
        if entrada[0][0] != '$':
            erro = f"Erro sintático: entrada não consumida completamente, restante: {entrada}"
            passos.append({
                'pilha': pilha.copy(),
                'entrada': [t[0] for t in entrada],
                'acao': f"ERRO: {erro}"
            })
            return False, erro, passos
        
        passos.append({
            'pilha': pilha.copy(),
            'entrada': [t[0] for t in entrada],
            'acao': "Análise concluída com sucesso!"
        })
        return True, "Análise sintática bem-sucedida!", passos