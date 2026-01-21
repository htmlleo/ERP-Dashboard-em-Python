import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas

# ================= SISTEMA =================

class ERP:
    def __init__(self, root):
        self.root = root
        self.root.title("ERP Dashboard PRO")
        self.root.geometry("1150x680")
        self.root.configure(bg="#1e1e2f")

        self.dados = []
        self.lixeira = []

        self.layout()

    # ================= LAYOUT =================

    def layout(self):
        topo = tk.Frame(self.root, bg="#27293d", height=60)
        topo.pack(fill="x")

        tk.Label(
            topo, text="ERP DASHBOARD PRO",
            fg="white", bg="#27293d",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        corpo = tk.Frame(self.root, bg="#1e1e2f")
        corpo.pack(fill="both", expand=True)

        self.formulario(corpo)
        self.tabela(corpo)

    # ================= FORM =================

    def formulario(self, frame):
        box = tk.LabelFrame(
            frame, text="Cadastro",
            bg="#1e1e2f", fg="white"
        )
        box.pack(fill="x", padx=10, pady=10)

        labels = ["Produto", "Categoria", "Preço", "Quantidade"]
        self.campos = {}

        for i, l in enumerate(labels):
            tk.Label(
                box, text=l,
                bg="#1e1e2f", fg="white"
            ).grid(row=0, column=i*2)

            self.campos[l] = tk.Entry(box, width=15)
            self.campos[l].grid(row=0, column=i*2+1, padx=5)

        tk.Label(box, text="Moeda",
                 bg="#1e1e2f", fg="white").grid(row=0, column=8)

        self.moeda = ttk.Combobox(
            box, values=["BRL", "USD", "EUR"],
            width=6, state="readonly"
        )
        self.moeda.set("BRL")
        self.moeda.grid(row=0, column=9, padx=5)

        tk.Label(box, text="Data",
                 bg="#1e1e2f", fg="white").grid(row=0, column=10)

        self.data = DateEntry(box)
        self.data.grid(row=0, column=11, padx=5)

        ttk.Button(box, text="Adicionar",
                   command=self.add).grid(row=1, column=1, pady=5)

        ttk.Button(box, text="Enviar p/ Lixeira",
                   command=self.enviar_lixeira).grid(row=1, column=3)

        ttk.Button(box, text="Restaurar",
                   command=self.restaurar).grid(row=1, column=5)

        ttk.Button(box, text="Excluir Permanente",
                   command=self.apagar).grid(row=1, column=7)

        ttk.Button(box, text="Exportar Excel",
                   command=self.excel).grid(row=1, column=9)

    # ================= TABELA =================

    def tabela(self, frame):
        col = ("Produto", "Categoria",
               "Preço", "Qtd",
               "Moeda", "Data")

        self.tree = ttk.Treeview(
            frame, columns=col,
            show="headings"
        )

        for c in col:
            self.tree.heading(c, text=c)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10, pady=10
        )

        box = tk.Frame(frame, bg="#1e1e2f")
        box.pack()

        ttk.Button(box, text="Gráfico Barra",
                   command=self.grafico_barra)\
            .grid(row=0, column=0, padx=5)

        ttk.Button(box, text="Gráfico Pizza",
                   command=self.grafico_pizza)\
            .grid(row=0, column=1, padx=5)

        ttk.Button(box, text="Exportar PDF",
                   command=self.pdf)\
            .grid(row=0, column=2, padx=5)

    # ================= FUNÇÕES =================

    def formatar(self, valor):
        return f"{valor:,.2f}".replace(",", "X")\
                              .replace(".", ",")\
                              .replace("X", ".")

    def add(self):
        try:
            preco = float(self.campos["Preço"].get())
            qtd = int(self.campos["Quantidade"].get())

            item = {
                "Produto": self.campos["Produto"].get(),
                "Categoria": self.campos["Categoria"].get(),
                "Preço": preco,
                "Qtd": qtd,
                "Moeda": self.moeda.get(),
                "Data": self.data.get()
            }

            self.dados.append(item)

            self.tree.insert(
                "", tk.END,
                values=(
                    item["Produto"],
                    item["Categoria"],
                    self.formatar(preco),
                    qtd,
                    item["Moeda"],
                    item["Data"]
                )
            )

            for c in self.campos.values():
                c.delete(0, "end")

        except:
            messagebox.showerror(
                "Erro",
                "Preencha os dados corretamente"
            )

    # ================= LIXEIRA =================

    def enviar_lixeira(self):
        sel = self.tree.selection()
        if not sel:
            return

        i = self.tree.index(sel)
        self.lixeira.append(self.dados.pop(i))
        self.tree.delete(sel)

    def restaurar(self):
        if not self.lixeira:
            return

        item = self.lixeira.pop()
        self.dados.append(item)

        self.tree.insert(
            "", tk.END,
            values=(
                item["Produto"],
                item["Categoria"],
                self.formatar(item["Preço"]),
                item["Qtd"],
                item["Moeda"],
                item["Data"]
            )
        )

    def apagar(self):
        sel = self.tree.selection()
        if not sel:
            return

        i = self.tree.index(sel)
        self.dados.pop(i)
        self.tree.delete(sel)

    # ================= EXPORTAR =================

    def excel(self):
        if not self.dados:
            messagebox.showwarning("Aviso", "Sem dados!")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )

        if caminho:
            df = pd.DataFrame(self.dados)
            df.to_excel(caminho, index=False)
            messagebox.showinfo("OK", "Excel salvo!")

    def pdf(self):
        if not self.dados:
            messagebox.showwarning("Aviso", "Sem dados!")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )

        if caminho:
            c = canvas.Canvas(caminho)
            y = 800

            for d in self.dados:
                linha = (
                    f'{d["Produto"]} | '
                    f'{d["Categoria"]} | '
                    f'{self.formatar(d["Preço"])} '
                    f'{d["Moeda"]}'
                )
                c.drawString(40, y, linha)
                y -= 20

            c.save()
            messagebox.showinfo("OK", "PDF salvo!")

    # ================= GRÁFICOS =================

    def grafico_barra(self):
        plt.close('all')
        df = pd.DataFrame(self.dados)
        df.groupby("Categoria")["Qtd"].sum()\
            .plot(kind="bar")

        plt.title("Quantidade por Categoria")
        plt.show()

    def grafico_pizza(self):
        plt.close('all')
        df = pd.DataFrame(self.dados)
        df.groupby("Categoria")["Qtd"].sum()\
            .plot(kind="pie", autopct="%1.0f%%")

        plt.title("Distribuição por Categoria")
        plt.show()


# ================= RUN =================

if __name__ == "__main__":
    root = tk.Tk()
    app = ERP(root)
    root.mainloop()
