import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import re
from analisador_sintatico import AnalisadorSintatico

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador Sintático Descendente Preditivo")
        self.root.geometry("900x700")
        
        self.analisador = AnalisadorSintatico()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para entrada
        entrada_frame = ttk.LabelFrame(main_frame, text="Entrada", padding="10")
        entrada_frame.pack(fill=tk.X, pady=5)
        
        # Campo de texto para entrada
        ttk.Label(entrada_frame, text="Digite a declaração de variáveis:").pack(anchor=tk.W)
        self.entrada_text = scrolledtext.ScrolledText(entrada_frame, width=80, height=5)
        self.entrada_text.pack(fill=tk.X, pady=5)
        self.entrada_text.insert(tk.END, "int a, b, c;")
        
        # Botão para analisar
        ttk.Button(entrada_frame, text="Analisar", command=self.analisar).pack(pady=5)
        
        # Frame para saída da análise
        saida_frame = ttk.LabelFrame(main_frame, text="Resultados da Análise", padding="10")
        saida_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Campo para mostrar tokens
        ttk.Label(saida_frame, text="Tokens:").pack(anchor=tk.W)
        self.tokens_text = scrolledtext.ScrolledText(saida_frame, width=80, height=5)
        self.tokens_text.pack(fill=tk.X, pady=5)
        
        # Campo para mostrar passos da análise
        ttk.Label(saida_frame, text="Passos da Análise:").pack(anchor=tk.W)
        self.passos_text = scrolledtext.ScrolledText(saida_frame, width=80, height=15)
        self.passos_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Campo para mostrar resultado
        ttk.Label(saida_frame, text="Resultado:").pack(anchor=tk.W)
        self.resultado_text = scrolledtext.ScrolledText(saida_frame, width=80, height=3)
        self.resultado_text.pack(fill=tk.X, pady=5)
        
        # Frame para tabela de análise
        tabela_frame = ttk.LabelFrame(main_frame, text="Tabela de Análise Preditiva", padding="10")
        tabela_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tabela de análise
        self.mostrar_tabela(tabela_frame)
        
    def mostrar_resultados_tabela(self, passos):
        # Cria um frame para a tabela
        tabela_frame = ttk.Frame(self.root)
        tabela_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cria a Treeview
        self.tree = ttk.Treeview(tabela_frame, columns=('Passo', 'Pilha', 'Entrada', 'Ação', 'Resultado'), show='headings')
        
        # Configura as colunas
        for col in ('Passo', 'Pilha', 'Entrada', 'Ação', 'Resultado'):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)
        
        # Adiciona os dados
        for passo in passos[1:]:  # Pula o cabeçalho
            self.tree.insert('', tk.END, values=(
                passo['Passo'],
                passo['Pilha'],
                passo['Entrada'],
                passo['Ação'],
                passo['Resultado']
            ))
        
        # Adiciona barra de rolagem
        scrollbar = ttk.Scrollbar(tabela_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Botão para exportar
        export_btn = ttk.Button(tabela_frame, text="Exportar para CSV", command=lambda: self.exportar_csv(passos))
        export_btn.pack(pady=5)

    def exportar_csv(self, passos):
        from datetime import datetime
        import csv
        
        filename = f"analise_sintatica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=passos[0].keys())
            writer.writeheader()
            writer.writerows(passos[1:])
        
        messagebox.showinfo("Exportado", f"Resultados exportados para {filename}")

        
    def analisar(self):
        entrada = self.entrada_text.get("1.0", tk.END).strip()
        self.tokens_text.delete("1.0", tk.END)
        self.passos_text.delete("1.0", tk.END)
        self.resultado_text.delete("1.0", tk.END)
        
        # Análise léxica
        tokens, erro_lexico = self.analisador.tokenizar(entrada)
        if erro_lexico:
            self.resultado_text.insert(tk.END, erro_lexico)
            self.resultado_text.tag_config("erro", foreground="red")
            self.resultado_text.tag_add("erro", "1.0", "end")
            return
        
        # Mostra tokens
        for token in tokens:
            self.tokens_text.insert(tk.END, f"{token[0]}: {token[1]}\n")
        
        # Análise sintática
        sucesso, mensagem, passos = self.analisador.analisar(tokens)
        
        # Mostra passos 
        for i, passo in enumerate(passos):
            pilha_str = ' '.join(passo['pilha'])
            entrada_str = ' '.join([f"{t[0]}:{t[1]}" for t in passo['entrada']])
            acao_str = passo['acao']
            
            posicao_inicio = self.passos_text.index(tk.END)
            self.passos_text.insert(tk.END, f"Passo {i+1}:\n")
            self.passos_text.insert(tk.END, f"  Pilha: {pilha_str}\n")
            self.passos_text.insert(tk.END, f"  Entrada: {entrada_str}\n")
            self.passos_text.insert(tk.END, f"  Ação: {acao_str}\n\n")
            
            # Destaca erros em vermelho
            if "ERRO" in acao_str:
                linha_acao = self.passos_text.search("  Ação:", posicao_inicio, tk.END)
                linha_fim = self.passos_text.index(f"{linha_acao} lineend")
                self.passos_text.tag_add("erro", linha_acao, linha_fim)
                self.passos_text.tag_config("erro", foreground="red")
        
        # Mostra resultado
        self.resultado_text.insert(tk.END, mensagem)
        if not sucesso:
            self.resultado_text.tag_config("erro", foreground="red")
            self.resultado_text.tag_add("erro", "1.0", "end")
        else:
            self.resultado_text.tag_config("sucesso", foreground="green")
            self.resultado_text.tag_add("sucesso", "1.0", "end")
    
    def mostrar_tabela(self, frame):
        # Cria uma tabela visual para a tabela de análise preditiva
        terminais = ['int', 'float', 'char', 'id', ',', ';', '$']
        
        # Cria o Treeview
        tree = ttk.Treeview(frame, columns=terminais, show='headings', height=10)
        
        # Configura as colunas
        for terminal in terminais:
            tree.heading(terminal, text=terminal)
            tree.column(terminal, width=100, anchor=tk.CENTER)
        
        # Adiciona os dados
        for nt in self.analisador.nao_terminais:
            valores = []
            for t in terminais:
                if nt in self.analisador.tabela and t in self.analisador.tabela[nt]:
                    valores.append(' '.join(self.analisador.tabela[nt][t]))
                else:
                    valores.append("")
            tree.insert('', tk.END, values=[nt] + valores, text=nt)
        
        # Adiciona uma barra de rolagem horizontal
        scrollbar_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscrollcommand=scrollbar_x.set)
        
        # Posiciona os elementos
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()
