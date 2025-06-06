import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, Toplevel
import os
import csv
from datetime import datetime

# Import ttkthemes for modern appearance
try:
    from ttkthemes import ThemedTk, ThemedStyle
    USE_THEMED_TK = True
except ImportError:
    USE_THEMED_TK = False
    print("For a more modern look, install ttkthemes: pip install ttkthemes")

# Import the analyzer (assuming this file exists and works as expected)
from analisador_sintatico import AnalisadorSintatico

class ModernSyntaxAnalyzerUI:
    def __init__(self, root):
        self.root = root
        
        # Initialize status variables first
        self.status_var = tk.StringVar(value="Ready")
        self.status_style = tk.StringVar(value="status.TLabel")
        
        # Setup UI components
        self.setup_window()
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        self.setup_bindings()
        
        # Initialize the analyzer
        self.analisador = AnalisadorSintatico()
        
        # Add example data to the input field
        self.input_text.insert("1.0", "int a, b, c;")
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Syntax Analyzer - Predictive Descent Parser")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Make the window responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # Give more space to content area
    
    def setup_styles(self):
        """Configure ttk styles for a more modern look"""
        if USE_THEMED_TK:
            self.style = ThemedStyle(self.root)
            self.style.set_theme("arc")  # A clean, modern theme
        else:
            self.style = ttk.Style()
        
        # Custom styles for different elements
        self.style.configure("TButton", padding=6)
        self.style.configure("Analyze.TButton", font=("Helvetica", 10, "bold"))
        self.style.configure("Title.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 10, "bold"))
        
        # Status styles
        self.style.configure("status.TLabel", padding=5)
        self.style.configure("success.TLabel", foreground="dark green", padding=5)
        self.style.configure("error.TLabel", foreground="dark red", padding=5)
    
    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Analysis", command=self.clear_all)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        """Create and arrange all UI widgets"""
        self.create_input_area()
        self.create_status_bar()
    
    def create_input_area(self):
        """Create the input area with text field and analyze button"""
        # Input frame with border and title
        input_frame = ttk.LabelFrame(self.root, text="Input Code", padding=(10, 5))
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        # Input text instructions
        input_label = ttk.Label(
            input_frame, 
            text="Enter your code below:",
            style="Header.TLabel"
        )
        input_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Frame for line numbers and text
        text_frame = ttk.Frame(input_frame)
        text_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Line numbers
        self.line_numbers = tk.Text(
            text_frame,
            width=4,
            padx=4,
            takefocus=0,
            border=0,
            background='lightgrey',
            state='disabled'
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        
        # Input text area with syntax highlighting cues
        self.input_text = scrolledtext.ScrolledText(
            text_frame, 
            height=20, 
            width=50, 
            font=("Consolas", 10),
            wrap="none",
            borderwidth=1, 
            relief="solid"
        )
        self.input_text.grid(row=0, column=1, sticky="nsew")
        
        # Bind events for line numbers
        self.input_text.bind("<KeyRelease>", self.update_line_numbers)
        self.input_text.bind("<MouseWheel>", self.update_line_numbers)
        
        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        
        # Analyze button
        self.analyze_button = ttk.Button(
            button_frame, 
            text="Analyze", 
            command=self.run_analysis,
            style="Analyze.TButton"
        )
        self.analyze_button.pack(side="right", padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_input
        )
        self.clear_button.pack(side="right", padx=5)
    
    def update_line_numbers(self, event=None):
        """Update the line numbers"""
        lines = self.input_text.get("1.0", "end-1c").split('\n')
        line_numbers_text = "\n".join(str(i+1) for i in range(len(lines)))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state='disabled')
        
        # Sync scrolling between text and line numbers
        self.line_numbers.yview_moveto(self.input_text.yview()[0])
    
    def create_status_bar(self):
        """Create the status bar for result feedback"""
        status_frame = ttk.Frame(self.root, relief="sunken", padding=(5, 2))
        status_frame.grid(row=2, column=0, sticky="ew")
        
        ttk.Label(status_frame, text="Status: ").pack(side="left")
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            style=self.status_style.get()
        )
        self.status_label.pack(side="left", fill="x", expand=True)
    
    def setup_bindings(self):
        """Set up keyboard shortcuts and event bindings"""
        self.root.bind("<F5>", lambda e: self.run_analysis())
        self.root.bind("<Control-n>", lambda e: self.clear_all())
        self.root.bind("<Control-e>", lambda e: self.export_results())
    
    def create_results_window(self):
        """Create a new window to display analysis results"""
        results_window = Toplevel(self.root)
        results_window.title("Analysis Results")
        results_window.geometry("1000x700")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(results_window)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        tokens_tab = ttk.Frame(notebook, padding=10)
        analysis_tab = ttk.Frame(notebook, padding=10)
        table_tab = ttk.Frame(notebook, padding=10)
        
        # Add tabs to notebook
        notebook.add(tokens_tab, text="Tokens")
        notebook.add(analysis_tab, text="Analysis Steps")
        notebook.add(table_tab, text="Predictive Table")
        
        # Configure tab content
        self.create_tokens_tab(tokens_tab)
        self.create_analysis_tab(analysis_tab)
        self.create_table_tab(table_tab)
        
        # Populate the predictive table
        self.populate_predictive_table()
        
        return results_window
    
    def create_tokens_tab(self, parent):
        """Setup the tokens display tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Tokens header
        ttk.Label(
            parent, 
            text="Lexical Analysis Results", 
            style="Title.TLabel"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Tokens display with headers
        token_frame = ttk.Frame(parent)
        token_frame.grid(row=1, column=0, sticky="nsew")
        token_frame.columnconfigure(0, weight=1)
        token_frame.rowconfigure(0, weight=1)
        
        # Use Treeview for token display
        columns = ("type", "value")
        self.tokens_tree = ttk.Treeview(
            token_frame, 
            columns=columns, 
            show="headings", 
            selectmode="browse"
        )
        
        # Configure columns
        self.tokens_tree.heading("type", text="Token Type")
        self.tokens_tree.heading("value", text="Value")
        self.tokens_tree.column("type", width=200)
        self.tokens_tree.column("value", width=200)
        
        # Add scrollbars
        tokens_scroll_y = ttk.Scrollbar(token_frame, orient="vertical", command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=tokens_scroll_y.set)
        
        # Grid layout
        self.tokens_tree.grid(row=0, column=0, sticky="nsew")
        tokens_scroll_y.grid(row=0, column=1, sticky="ns")
    
    def create_analysis_tab(self, parent):
        """Setup the analysis steps display tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Analysis header
        ttk.Label(
            parent, 
            text="Syntax Analysis Steps", 
            style="Title.TLabel"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Analysis steps in a treeview with columns
        columns = ("step", "stack", "input", "action")
        self.analysis_tree = ttk.Treeview(
            parent, 
            columns=columns, 
            show="headings", 
            selectmode="browse"
        )
        
        # Configure columns
        self.analysis_tree.heading("step", text="Step")
        self.analysis_tree.heading("stack", text="Stack")
        self.analysis_tree.heading("input", text="Remaining Input")
        self.analysis_tree.heading("action", text="Action")
        
        self.analysis_tree.column("step", width=50, anchor="center")
        self.analysis_tree.column("stack", width=200)
        self.analysis_tree.column("input", width=300)
        self.analysis_tree.column("action", width=300)
        
        # Add scrollbars
        analysis_scroll_y = ttk.Scrollbar(
            parent, 
            orient="vertical", 
            command=self.analysis_tree.yview
        )
        analysis_scroll_x = ttk.Scrollbar(
            parent, 
            orient="horizontal", 
            command=self.analysis_tree.xview
        )
        
        self.analysis_tree.configure(
            yscrollcommand=analysis_scroll_y.set,
            xscrollcommand=analysis_scroll_x.set
        )
        
        # Grid layout
        self.analysis_tree.grid(row=1, column=0, sticky="nsew")
        analysis_scroll_y.grid(row=1, column=1, sticky="ns")
        analysis_scroll_x.grid(row=2, column=0, sticky="ew")
    
    def create_table_tab(self, parent):
        """Setup the predictive parsing table tab"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Table header
        ttk.Label(
            parent, 
            text="LL(1) Predictive Parsing Table", 
            style="Title.TLabel"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Create a frame for the table with scrollbars
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create the table (will be populated later)
        self.predictive_table = ttk.Treeview(table_frame)
        
        # Add scrollbars
        table_scroll_y = ttk.Scrollbar(
            table_frame, 
            orient="vertical", 
            command=self.predictive_table.yview
        )
        table_scroll_x = ttk.Scrollbar(
            table_frame, 
            orient="horizontal", 
            command=self.predictive_table.xview
        )
        
        self.predictive_table.configure(
            yscrollcommand=table_scroll_y.set,
            xscrollcommand=table_scroll_x.set
        )
        
        # Grid layout
        self.predictive_table.grid(row=0, column=0, sticky="nsew")
        table_scroll_y.grid(row=0, column=1, sticky="ns")
        table_scroll_x.grid(row=1, column=0, sticky="ew")
    
    def populate_predictive_table(self):
        """Populate the predictive parsing table with grammar rules"""
        # Define terminal symbols
        terminais = ['int', 'float', 'char', 'id', ',', ';', '$']
        
        # Setup columns
        columns = ['non_terminal'] + terminais
        self.predictive_table["columns"] = columns
        self.predictive_table["show"] = "headings"
        
        # Configure headers
        self.predictive_table.heading("non_terminal", text="Non-Terminal")
        for terminal in terminais:
            self.predictive_table.heading(terminal, text=terminal)
            self.predictive_table.column(terminal, width=100, anchor="center")
        
        # Special styling for non-terminal column
        self.predictive_table.column("non_terminal", width=150, anchor="w")
        
        # Add data rows
        for nt in self.analisador.nao_terminais:
            values = [nt]  # Start with non-terminal
            for t in terminais:
                if nt in self.analisador.tabela and t in self.analisador.tabela[nt]:
                    values.append(' '.join(self.analisador.tabela[nt][t]))
                else:
                    values.append("")
            self.predictive_table.insert('', 'end', values=values)
    
    def run_analysis(self):
        """Execute the syntax analysis and update the UI"""
        # Create results window
        results_window = self.create_results_window()
        
        # Clear previous results
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        
        # Get input text
        entrada = self.input_text.get("1.0", tk.END).strip()
        if not entrada:
            self.set_status("Please enter code to analyze", "error")
            return
        
        # Lexical analysis
        tokens, erro_lexico = self.analisador.tokenizar(entrada)
        if erro_lexico:
            self.set_status(f"Lexical Error: {erro_lexico}", "error")
            return
        
        # Display tokens
        for i, token in enumerate(tokens):
            self.tokens_tree.insert('', 'end', values=(token[0], token[1]))
        
        # Syntax analysis
        sucesso, mensagem, passos = self.analisador.analisar(tokens)
        
        # Display analysis steps
        for i, passo in enumerate(passos):
            pilha_str = ' '.join(passo['pilha'])
            entrada_str = ' '.join([f"{t[0]}:{t[1]}" for t in passo['entrada']])
            acao_str = passo['acao']
            
            item_id = self.analysis_tree.insert('', 'end', values=(
                i+1, pilha_str, entrada_str, acao_str
            ))
            
            # Highlight errors in red
            if "ERRO" in acao_str:
                self.analysis_tree.item(item_id, tags=("error",))
        
        # Configure tag for error highlighting
        self.analysis_tree.tag_configure("error", background="#ffcccc")
        
        # Update status
        self.set_status(mensagem, "success" if sucesso else "error")
        
        # Bring results window to front
        results_window.lift()
    
    def set_status(self, message, style="status"):
        """Update the status bar with message and appropriate style"""
        self.status_var.set(message)
        self.status_style.set(f"{style}.TLabel")
        self.status_label.configure(style=f"{style}.TLabel")
    
    def clear_input(self):
        """Clear only the input field"""
        self.input_text.delete("1.0", tk.END)
        self.update_line_numbers()
        self.set_status("Ready", "status")
    
    def clear_all(self):
        """Clear all inputs and results"""
        self.clear_input()
    
    def export_results(self):
        """Export analysis results to CSV file"""
        # Check if there are results to export
        if not hasattr(self, 'analysis_tree') or not self.analysis_tree.get_children():
            messagebox.showinfo("Export", "No analysis results to export.")
            return
        
        # Get file location from user
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"syntax_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            initialdir=os.path.abspath("./exports")
        )
        
        if not filename:
            return  # User canceled
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write headers
                writer.writerow(["Step", "Stack", "Input", "Action"])
                
                # Write data rows
                for item_id in self.analysis_tree.get_children():
                    values = self.analysis_tree.item(item_id, "values")
                    writer.writerow(values)
            
            self.set_status(f"Results exported to {os.path.basename(filename)}", "success")
            messagebox.showinfo("Export Successful", f"Results exported to {filename}")
            
        except Exception as e:
            self.set_status(f"Export failed: {str(e)}", "error")
            messagebox.showerror("Export Failed", f"Error exporting results: {str(e)}")


def main():
    """Start the application"""
    if USE_THEMED_TK:
        root = ThemedTk(theme="arc")
    else:
        root = tk.Tk()
    
    app = ModernSyntaxAnalyzerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()