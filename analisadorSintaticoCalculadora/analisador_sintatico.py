import sys
from pathlib import Path

class AnalisadorSintatico:
    def __init__(self):
        # Definição dos símbolos terminais e não-terminais
        self.terminais = [
            'program', 'const', 'var', 'procedure', 'function', 'begin', 'end', 
            'if', 'then', 'else', 'while', 'do', 'repeat', 'until', 'for', 'to',
            'read', 'write', 'integer', 'real', 'char', 'id', 'num_int', 'num_real',
            '(', ')', '*', '/', '+', '-', '>', '<', '=', '<>', '>=', '<=', ':=', 
            '$', ';', ':', ',', '.', "'"
        ]
        
        self.nao_terminais = [
            'PROGRAMA', 'CORPO', 'DC', 'DC_C', 'DC_V', 'DC_P', 'DC_FUNC',
            'TIPO_VAR', 'VARIAVEIS', 'MAIS_VAR', 'PARAMETROS', 'LISTA_PAR',
            'MAIS_PAR', 'CORPO_P', 'DC_LOC', 'LISTA_ARG', 'ARGUMENTOS',
            'MAIS_IDENT', 'PFALSA', 'COMANDOS', 'CMD', 'CONDICAO', 'RELACAO',
            'EXPRESSAO', 'OP_UN', 'OUTROS_TERMOS', 'OP_AD', 'TERMO',
            'MAIS_FATORES', 'OP_MUL', 'FATOR', 'NUMERO'
        ]
        
        # Tabela de análise preditiva LL(1)
        self.tabela = {
            # Programa principal
            'PROGRAMA': {
                'program': ['program', 'id', ';', 'CORPO', '.']
            },
            
            # Corpo do programa
            'CORPO': {
                'const': ['DC', 'begin', 'COMANDOS', 'end'],
                'var': ['DC', 'begin', 'COMANDOS', 'end'],
                'procedure': ['DC', 'begin', 'COMANDOS', 'end'],
                'function': ['DC', 'begin', 'COMANDOS', 'end'],
                'begin': ['DC', 'begin', 'COMANDOS', 'end']
            },
            
            # Declarações
            'DC': {
                'const': ['DC_C', 'DC_V', 'DC_P', 'DC_FUNC'],
                'var': ['DC_C', 'DC_V', 'DC_P', 'DC_FUNC'],
                'procedure': ['DC_C', 'DC_V', 'DC_P', 'DC_FUNC'],
                'function': ['DC_C', 'DC_V', 'DC_P', 'DC_FUNC'],
                'begin': ['ε']
            },
            
            # Declarações de constantes
            'DC_C': {
                'const': ['const', 'id', '=', 'NUMERO', ';', 'DC_C'],
                'var': ['ε'],
                'procedure': ['ε'],
                'function': ['ε'],
                'begin': ['ε']
            },
            
            # Declarações de variáveis
            'DC_V': {
                'var': ['var', 'VARIAVEIS', ':', 'TIPO_VAR', ';', 'DC_V'],
                'procedure': ['ε'],
                'function': ['ε'],
                'begin': ['ε']
            },
            
            'TIPO_VAR': {
                'integer': ['integer'],
                'real': ['real'],
                'char': ['char']
            },
            
            'VARIAVEIS': {
                'id': ['id', 'MAIS_VAR']
            },
            
            'MAIS_VAR': {
                ',': [',', 'VARIAVEIS'],
                ':': ['ε'],
                ')': ['ε']
            },
            
            # Declarações de procedimentos
            'DC_P': {
                'procedure': ['procedure', 'id', 'PARAMETROS', ';', 'CORPO_P', 'DC_P'],
                'function': ['ε'],
                'begin': ['ε']
            },
            
            # Declarações de funções
            'DC_FUNC': {
                'function': ['function', 'id', 'PARAMETROS', ':', 'TIPO_VAR', ';', 'CORPO_P', 'DC_FUNC'],
                'begin': ['ε']
            },
            
            'PARAMETROS': {
                '(': ['(', 'LISTA_PAR', ')'],
                ';': ['ε'],
                ':': ['ε']
            },
            
            'LISTA_PAR': {
                'id': ['VARIAVEIS', ':', 'TIPO_VAR', 'MAIS_PAR'],
                ')': ['ε']
            },
            
            'MAIS_PAR': {
                ';': [';', 'LISTA_PAR'],
                ')': ['ε']
            },
            
            'CORPO_P': {
                'const': ['DC_LOC', 'begin', 'COMANDOS', 'end', ';'],
                'var': ['DC_LOC', 'begin', 'COMANDOS', 'end', ';'],
                'begin': ['DC_LOC', 'begin', 'COMANDOS', 'end', ';']
            },
            
            'DC_LOC': {
                'const': ['DC_C', 'DC_V'],
                'var': ['DC_V'],
                'begin': ['ε']
            },
            
            # Comandos
            'COMANDOS': {
                'id': ['CMD', ';', 'COMANDOS'],
                'read': ['CMD', ';', 'COMANDOS'],
                'write': ['CMD', ';', 'COMANDOS'],
                'while': ['CMD', ';', 'COMANDOS'],
                'if': ['CMD', ';', 'COMANDOS'],
                'begin': ['CMD', ';', 'COMANDOS'],
                'repeat': ['CMD', ';', 'COMANDOS'],
                'for': ['CMD', ';', 'COMANDOS'],
                'end': ['ε'],
                'until': ['ε']
            },
            
            'CMD': {
                'id': ['id', 'CMD_CONT'],
                'read': ['read', '(', 'VARIAVEIS', ')'],
                'write': ['write', '(', 'VARIAVEIS', ')'],
                'while': ['while', '(', 'CONDICAO', ')', 'do', 'CMD'],
                'if': ['if', 'CONDICAO', 'then', 'CMD', 'PFALSA'],
                'begin': ['begin', 'COMANDOS', 'end'],
                'repeat': ['repeat', 'COMANDOS', 'until', 'CONDICAO'],
                'for': ['for', 'id', ':=', 'EXPRESSAO', 'to', 'num_int', 'do', 'begin', 'COMANDOS', 'end']
            },
            
            'CMD_CONT': {
                ':=': [':=', 'EXPRESSAO'],
                '(': ['LISTA_ARG']
            },
            
            'LISTA_ARG': {
                '(': ['(', 'ARGUMENTOS', ')'],
                ';': ['ε'],
                'end': ['ε'],
                'until': ['ε']
            },
            
            'ARGUMENTOS': {
                'id': ['id', 'MAIS_IDENT'],
                ')': ['ε']
            },
            
            'MAIS_IDENT': {
                ',': [',', 'ARGUMENTOS'],
                ')': ['ε']
            },
            
            'PFALSA': {
                'else': ['else', 'CMD'],
                ';': ['ε'],
                'end': ['ε'],
                'until': ['ε']
            },
            
            # Condições
            'CONDICAO': {
                'id': ['EXPRESSAO', 'RELACAO', 'EXPRESSAO'],
                '(': ['EXPRESSAO', 'RELACAO', 'EXPRESSAO'],
                '+': ['EXPRESSAO', 'RELACAO', 'EXPRESSAO'],
                '-': ['EXPRESSAO', 'RELACAO', 'EXPRESSAO'],
                'num_int': ['EXPRESSAO', 'RELACAO', 'EXPRESSAO'],
                'num_real': ['EXPRESSAO', 'RELACAO', 'EXPRESSAO'],
                "'": ['EXPRESSAO', 'RELACAO', 'EXPRESSAO']
            },
            
            'RELACAO': {
                '=': ['='],
                '<>': ['<>'],
                '>=': ['>='],
                '<=': ['<='],
                '>': ['>'],
                '<': ['<']
            },
            
            # Expressões
            'EXPRESSAO': {
                'id': ['TERMO', 'OUTROS_TERMOS'],
                '(': ['TERMO', 'OUTROS_TERMOS'],
                '+': ['OP_UN', 'TERMO', 'OUTROS_TERMOS'],
                '-': ['OP_UN', 'TERMO', 'OUTROS_TERMOS'],
                'num_int': ['TERMO', 'OUTROS_TERMOS'],
                'num_real': ['TERMO', 'OUTROS_TERMOS'],
                "'": ['TERMO', 'OUTROS_TERMOS']
            },
            
            'OP_UN': {
                '+': ['+'],
                '-': ['-'],
                'id': ['ε'],
                '(': ['ε'],
                'num_int': ['ε'],
                'num_real': ['ε'],
                "'": ['ε']
            },
            
            'OUTROS_TERMOS': {
                '+': ['OP_AD', 'TERMO', 'OUTROS_TERMOS'],
                '-': ['OP_AD', 'TERMO', 'OUTROS_TERMOS'],
                ')': ['ε'],
                ';': ['ε'],
                ',': ['ε'],
                '=': ['ε'],
                '<>': ['ε'],
                '>=': ['ε'],
                '<=': ['ε'],
                '>': ['ε'],
                '<': ['ε'],
                'then': ['ε'],
                'do': ['ε'],
                'until': ['ε'],
                'to': ['ε']
            },
            
            'OP_AD': {
                '+': ['+'],
                '-': ['-']
            },
            
            'TERMO': {
                'id': ['FATOR', 'MAIS_FATORES'],
                '(': ['FATOR', 'MAIS_FATORES'],
                'num_int': ['FATOR', 'MAIS_FATORES'],
                'num_real': ['FATOR', 'MAIS_FATORES'],
                "'": ['FATOR', 'MAIS_FATORES']
            },
            
            'MAIS_FATORES': {
                '*': ['OP_MUL', 'FATOR', 'MAIS_FATORES'],
                '/': ['OP_MUL', 'FATOR', 'MAIS_FATORES'],
                '+': ['ε'],
                '-': ['ε'],
                ')': ['ε'],
                ';': ['ε'],
                ',': ['ε'],
                '=': ['ε'],
                '<>': ['ε'],
                '>=': ['ε'],
                '<=': ['ε'],
                '>': ['ε'],
                '<': ['ε'],
                'then': ['ε'],
                'do': ['ε'],
                'until': ['ε'],
                'to': ['ε']
            },
            
            'OP_MUL': {
                '*': ['*'],
                '/': ['/']
            },
            
            'FATOR': {
                'id': ['id'],
                '(': ['(', 'EXPRESSAO', ')'],
                'num_int': ['num_int'],
                'num_real': ['num_real'],
                "'": ["'", 'char', "'"]
            },
            
            'NUMERO': {
                'num_int': ['num_int'],
                'num_real': ['num_real']
            }
        }
    
    def tokenizar(self, entrada):
        """
        Converte os tokens do analisador léxico para o formato usado pelo analisador sintático
        """
        # Adiciona o caminho do módulo lexico ao PATH do Python
        sys.path.append(str(Path(__file__).parent.parent / "AnalisadorLexicoLALG (2)" / "AnalisadorLexicoLALG"))

        from analisador_lexico_texto import AnalisadorLexicoTexto
        
        analisador_lexico = AnalisadorLexicoTexto(entrada)
        analisador_lexico.analisar()
        
        if analisador_lexico.erros:
            return None, analisador_lexico.erros[0]
        
        # Mapeia os tokens do analisador léxico para os tokens do sintático
        tokens = []
        token_map = {
            # Tokens de símbolos simples (tok1XX)
            'tok100': '(',
            'tok101': ')',
            'tok102': '*',
            'tok103': '/',
            'tok104': '+',
            'tok105': '-',
            'tok106': '>',
            'tok107': '<',
            'tok108': '=',
            'tok109': '$',
            'tok110': ';',
            'tok111': ':',
            'tok112': ',',
            'tok113': '.',
            
            # Tokens de símbolos duplos (tok2XX)
            'tok200': '<>',
            'tok201': '>=',
            'tok202': '<=',
            'tok203': ':=',
            
            # Tokens de números (tok3XX)
            'tok300': 'num_int',
            'tok301': 'num_real',
            
            # Tokens de palavras reservadas (tok4XX)
            'tok400': 'program',
            'tok401': 'var',
            'tok402': 'procedure',
            'tok403': 'if',
            'tok404': 'then',
            'tok405': 'while',
            'tok406': 'do',
            'tok407': 'write',
            'tok408': 'read',
            'tok409': 'else',
            'tok410': 'begin',
            'tok411': 'end',
            'tok412': 'integer',
            'tok413': 'real',
            
            # Token de identificador (tok500)
            'tok500': 'id'
        }
        
        # Converter tokens para o formato usado pelo analisador sintático
        for token in analisador_lexico.tokens:
            codigo_token = token[0]
            valor = token[1]
            linha = token[2]
            coluna_ini = token[3]
            coluna_fim = token[4]
            
            if codigo_token in token_map:
                tipo_token = token_map[codigo_token]
                tokens.append((tipo_token, valor, linha, coluna_ini, coluna_fim))
            else:
                return None, f"Token desconhecido: {codigo_token} - {valor}"
        
        # Adicionar marcador de fim
        tokens.append(('$', '$', 0, 0, 0))
        return tokens, None
    
    def analisar(self, tokens):
        # Inicializa a pilha com o símbolo de início e de fim
        pilha = ['$', 'PROGRAMA']
        entrada = tokens.copy()
        passos = []
        
        token_atual_idx = 0
        
        while len(pilha) > 0:
            topo = pilha[-1]
            if token_atual_idx >= len(entrada):
                token_atual = '$'
                token_valor = '$'
                token_linha = 0
                token_coluna = 0
            else:
                token_atual, token_valor, token_linha, token_coluna_ini, token_coluna_fim = entrada[token_atual_idx]
            
            # Registrar passo
            passos.append({
                'pilha': pilha.copy(),
                'entrada': entrada[token_atual_idx:],
                'acao': ''
            })
            
            # Se o topo da pilha é um terminal
            if topo in self.terminais:
                if topo == token_atual:
                    pilha.pop()
                    token_atual_idx += 1
                    passos[-1]['acao'] = f"Consumir {token_valor}"
                else:
                    erro = f"Erro sintático: esperado '{topo}', encontrado '{token_valor}' na linha {token_linha}, coluna {token_coluna_ini}"
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
                    # Verifica quais tokens são esperados para esse não-terminal
                    esperados = list(self.tabela.get(topo, {}).keys())
                    erro = f"Erro sintático na linha {token_linha}, coluna {token_coluna_ini}: não há produção para {topo} com entrada {token_valor}. Esperado: {', '.join(esperados)}"
                    passos[-1]['acao'] = f"ERRO: {erro}"
                    return False, erro, passos
            else:
                erro = f"Erro sintático: símbolo desconhecido na pilha '{topo}'"
                passos[-1]['acao'] = f"ERRO: {erro}"
                return False, erro, passos
        
        # Verifica se a análise foi concluída com sucesso
        if token_atual_idx >= len(entrada) - 1:  # -1 para ignorar o token $ que adicionamos
            passos.append({
                'pilha': [],
                'entrada': [],
                'acao': "Análise concluída com sucesso!"
            })
            return True, "Análise sintática bem-sucedida!", passos
        else:
            erro = f"Erro sintático: entrada não foi completamente analisada. Token restante: {entrada[token_atual_idx][1]} na linha {entrada[token_atual_idx][2]}"
            passos.append({
                'pilha': pilha.copy(),
                'entrada': entrada[token_atual_idx:],
                'acao': f"ERRO: {erro}"
            })
            return False, erro, passos