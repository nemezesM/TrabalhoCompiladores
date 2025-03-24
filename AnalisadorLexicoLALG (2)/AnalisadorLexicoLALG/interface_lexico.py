import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from analisador_lexico_texto import AnalisadorLexicoTexto  # certifique-se que esse arquivo está correto

class InterfaceLexico:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador Léxico - LALG")
        self.root.geometry("900x850")
        self.criar_widgets()

    def criar_widgets(self):
        # Frame com numeração de linha + código
        frame_codigo = tk.Frame(self.root)
        frame_codigo.pack(fill=tk.BOTH, expand=False)

        # Área de linha (numerador)
        self.numeros_linha = tk.Text(frame_codigo, width=4, padx=3, takefocus=0, border=0,
                                     background='#eeeeee', state='disabled', wrap='none')
        self.numeros_linha.pack(side=tk.LEFT, fill=tk.Y)

        # Área de código
        self.texto_codigo = ScrolledText(frame_codigo, height=15, font=("Courier New", 11), wrap=tk.NONE)
        self.texto_codigo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.texto_codigo.bind("<KeyRelease>", self.atualizar_linhas)

        # Botões
        botoes_frame = tk.Frame(self.root)
        botoes_frame.pack(pady=5)

        btn_importar = tk.Button(botoes_frame, text="📂 Importar Arquivo", command=self.importar_arquivo)
        btn_importar.grid(row=0, column=0, padx=5)

        btn_salvar = tk.Button(botoes_frame, text="💾 Salvar Arquivo", command=self.salvar_arquivo)
        btn_salvar.grid(row=0, column=1, padx=5)

        btn_analisar = tk.Button(botoes_frame, text="🔍 Analisar Léxico", command=self.analisar_lexico)
        btn_analisar.grid(row=0, column=2, padx=5)

        btn_exportar = tk.Button(botoes_frame, text="📤 Exportar Tabela", command=self.exportar_tabela)
        btn_exportar.grid(row=0, column=3, padx=5)

        # Tabela de tokens (Treeview)
        self.tree = ttk.Treeview(self.root, columns=("Token", "Lexema", "Linha"), show="headings", height=12)
        self.tree.heading("Token", text="Token")
        self.tree.heading("Lexema", text="Lexema")
        self.tree.heading("Linha", text="Linha")

        self.tree.column("Token", width=100)
        self.tree.column("Lexema", width=250)
        self.tree.column("Linha", width=100)

        self.tree.pack(padx=10, pady=(10, 2), fill=tk.BOTH, expand=False)

        # Área de erros
        self.texto_erros = ScrolledText(self.root, height=5, bg="#fff0f0", font=("Courier New", 10))
        self.texto_erros.pack(padx=10, pady=(2, 10), fill=tk.BOTH, expand=False)
        self.texto_erros.insert(tk.END, ">> Erros Léxicos\n")

    def atualizar_linhas(self, event=None):
        linhas = self.texto_codigo.get("1.0", "end-1c").split("\n")
        conteudo_linhas = "\n".join(str(i+1) for i in range(len(linhas)))
        self.numeros_linha.config(state='normal')
        self.numeros_linha.delete("1.0", tk.END)
        self.numeros_linha.insert("1.0", conteudo_linhas)
        self.numeros_linha.config(state='disabled')

    def importar_arquivo(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos LALG", "*.lalg"), ("Todos os arquivos", "*.*")])
        if caminho:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                self.texto_codigo.delete(1.0, tk.END)
                self.texto_codigo.insert(tk.END, conteudo)
            self.atualizar_linhas()

    def salvar_arquivo(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".lalg", filetypes=[("Arquivos LALG", "*.lalg")])
        if caminho:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(self.texto_codigo.get(1.0, tk.END))
            messagebox.showinfo("Salvo", "Arquivo salvo com sucesso!")

    def exportar_tabela(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivo texto", "*.txt")])
        if caminho:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write("Tabela de Tokens\n")
                for item in self.tree.get_children():
                    valores = self.tree.item(item, 'values')
                    f.write(f"{valores[0]}_{valores[1]} => Linha {valores[2]}\n")
            messagebox.showinfo("Exportado", "Tabela exportada com sucesso!")

    def analisar_lexico(self):
        codigo = self.texto_codigo.get("1.0", tk.END)
        analisador = AnalisadorLexicoTexto(codigo)
        analisador.analisar()

        # Preencher a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        for token in analisador.tokens:
            self.tree.insert("", tk.END, values=(token[0], token[1], token[2]))

        # Preencher a área de erros
        self.texto_erros.delete("1.0", tk.END)
        self.texto_erros.insert(tk.END, ">> Erros Léxicos\n")
        if not analisador.erros:
            self.texto_erros.insert(tk.END, "Nenhum erro encontrado.\n")
        else:
            for erro in analisador.erros:
                self.texto_erros.insert(tk.END, erro + "\n")

# Executar a interface
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceLexico(root)
    root.mainloop()
