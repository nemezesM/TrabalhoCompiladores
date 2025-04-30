class AnalisadorSintatico:
    def __init__(self):
        # Definição dos símbolos terminais e não-terminais
        self.terminais = ['TIPO', 'id', ',', ';', '$']
        self.nao_terminais = ['P', 'DECL', 'LISTA_ID', 'LISTA_ID_']
        
        # Tabela de análise preditiva corrigida
        self.tabela = {
            'P': {
                'TIPO': ['DECL'],
                '$': ['ε']
            },
            'DECL': {
                'TIPO': ['TIPO', 'LISTA_ID', ';']
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
        pilha = ['$', 'P']
        entrada = tokens.copy()
        passos = []
        
        while len(pilha) > 0 and pilha[-1] != '$':
            topo = pilha[-1]
            if not entrada:
                token_atual = '$'
                token_valor = '$'
            else:
                token_atual, token_valor = entrada[0]
            
            # Registrar passo
            passos.append({
                'pilha': pilha.copy(),
                'entrada': entrada.copy(),
                'acao': ''
            })
            
            # Se o topo da pilha é um terminal
            if topo in self.terminais:
                if topo == token_atual:
                    pilha.pop()
                    if entrada:
                        entrada.pop(0)
                    passos[-1]['acao'] = f"Consumir {token_valor}"
                else:
                    erro = f"Erro sintático: esperado '{topo}', encontrado '{token_valor}'"
                    passos[-1]['acao'] = f"ERRO: {erro}"
                    return False, erro, passos
            
            # Se o topo da pilha é epsilon
            elif topo == 'ε':
                pilha.pop()
                passos[-1]['acao'] = "Remover ε"
            
            # Se o topo da pilha é um não-terminal
            elif topo in self.nao_terminais:
                if token_atual in self.tabela.get(topo, {}):
                    producao = self.tabela[topo][token_atual]
                    pilha.pop()
                    # Adiciona a produção na ordem inversa
                    for simbolo in reversed(producao):
                        if simbolo != 'ε':
                            pilha.append(simbolo)
                    passos[-1]['acao'] = f"Expandir {topo} -> {' '.join(producao)}"
                else:
                    esperados = list(self.tabela.get(topo, {}).keys())
                    erro = f"Erro sintático: não há produção para {topo} com entrada {token_valor}. Esperado: {esperados}"
                    passos[-1]['acao'] = f"ERRO: {erro}"
                    return False, erro, passos
            else:
                erro = f"Erro sintático: símbolo desconhecido na pilha '{topo}'"
                passos[-1]['acao'] = f"ERRO: {erro}"
                return False, erro, passos
        
        # Verifica se a análise foi concluída com sucesso
        if (not entrada or entrada[0][0] == '$') and (not pilha or pilha[-1] == '$'):
            passos.append({
                'pilha': ['$'],
                'entrada': [('$', '$')],
                'acao': "Análise concluída com sucesso!"
            })
            return True, "Análise sintática bem-sucedida!", passos
        else:
            erro = "Erro sintático: entrada não foi completamente analisada"
            passos.append({
                'pilha': pilha.copy(),
                'entrada': [(t[0], t[1]) for t in entrada],
                'acao': f"ERRO: {erro}"
            })
            return False, erro, passos