import string

class AnalisadorLexicoTexto:
    def __init__(self, texto):
        self.codigo = texto.splitlines()
        self.tokens = []
        self.erros = []

    def eh_simbolo_simples(self, c):
        return c in "()*/+-><=$;:,."

    def token_simples(self, c):
        simples = "()*/+-><=$;:,."
        i = simples.find(c)
        return f"tok1{str(i).zfill(2)}"

    def eh_duplo(self, s):
        return s in ["<>", ">=", "<=", ":="]

    def token_duplo(self, s):
        duplos = ["<>", ">=", "<=", ":="]
        i = duplos.index(s)
        return f"tok20{str(i)}"

    def eh_reservada(self, palavra):
        return palavra in ["program", "var", "procedure", "if", "then", "while", "do",
                           "write", "read", "else", "begin", "end", "integer", "real"]

    def token_reservada(self, palavra):
        reservadas = ["program", "var", "procedure", "if", "then", "while", "do",
                      "write", "read", "else", "begin", "end", "integer", "real"]
        i = reservadas.index(palavra)
        return f"tok4{str(i).zfill(2)}"

    def eh_letra(self, c):
        return c in string.ascii_letters

    def eh_digito(self, c):
        return c in "0123456789"

    def analisar(self):
        for num_linha, linha in enumerate(self.codigo, start=1):
            i = 0
            tamanho = len(linha)
            while i < tamanho:
                c = linha[i]
                prox = linha[i + 1] if i + 1 < tamanho else ""
                coluna_ini = i + 1  # 1-based

                # Comentário por {}
                if c == '{':
                    while i < tamanho and linha[i] != '}':
                        i += 1
                    if i == tamanho:
                        self.erros.append(f"Erro Léxico - Comentário não fechado - linha {num_linha}")
                    i += 1
                    continue

                # Comentário por /* */
                elif c == '/' and prox == '*':
                    i += 2
                    fechado = False
                    while num_linha <= len(self.codigo):
                        while i < len(linha):
                            if linha[i] == '*' and i + 1 < len(linha) and linha[i + 1] == '/':
                                i += 2
                                fechado = True
                                break
                            i += 1
                        if fechado:
                            break
                        num_linha += 1
                        if num_linha - 1 < len(self.codigo):
                            linha = self.codigo[num_linha - 1]
                            i = 0
                        else:
                            break
                    if not fechado:
                        self.erros.append(f"Erro Léxico - Comentário não fechado - linha {num_linha}")
                    continue

                elif self.eh_duplo(c + prox):
                    self.tokens.append((self.token_duplo(c + prox), c + prox, num_linha, coluna_ini, coluna_ini + 1))
                    i += 2
                    continue

                elif self.eh_simbolo_simples(c):
                    self.tokens.append((self.token_simples(c), c, num_linha, coluna_ini, coluna_ini))
                    i += 1
                    continue

                elif self.eh_digito(c):
                    num = c
                    i += 1
                    while i < tamanho and self.eh_digito(linha[i]):
                        num += linha[i]
                        i += 1
                    if i < tamanho and linha[i] == '.':
                        num += '.'
                        i += 1
                        if i < tamanho and self.eh_digito(linha[i]):
                            while i < tamanho and self.eh_digito(linha[i]):
                                num += linha[i]
                                i += 1
                            self.tokens.append(("tok301", num, num_linha, coluna_ini, coluna_ini + len(num) - 1))
                        else:
                            self.erros.append(f"Erro Léxico - Número real mal formado - linha {num_linha}")
                    else:
                        self.tokens.append(("tok300", num, num_linha, coluna_ini, coluna_ini + len(num) - 1))
                    continue

                elif self.eh_letra(c):
                    ident = c
                    i += 1
                    while i < tamanho and (self.eh_letra(linha[i]) or self.eh_digito(linha[i]) or linha[i] == "_"):
                        ident += linha[i]
                        i += 1
                    tipo = self.token_reservada(ident) if self.eh_reservada(ident) else "tok500"
                    self.tokens.append((tipo, ident, num_linha, coluna_ini, coluna_ini + len(ident) - 1))
                    continue

                elif c in [' ', '\t', '\n', '\r']:
                    i += 1
                    continue

                else:
                    self.erros.append(f"Erro Léxico: Caractere inválido '{c}' - linha {num_linha}")
                    i += 1
