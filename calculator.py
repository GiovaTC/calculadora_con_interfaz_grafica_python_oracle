# History listbox
lbl = ttk.Label(self, text=" historial (oracle) : ")
lbl.grid(row=0, column=4, padx=(10,0), pady=(10,0), sticky="nw")

self.history_lb = tk.Listbox(self, height=25, width=45)
self.history_lb.grid(row=1, column=4, rowspan=6, padx=(10,10), pady=10, sticky="nsew")
self.history_lb.bind("<Double-Button-1>", self._on_history_double_click)

def _on_button_click(self, label):
    if label == "c":
        self.display_var.set("")
    elif label == "=":
        expr = self.display_var.get().strip()
        if not expr:
            return
        try:
            result = safe_eval(expr)
            # formatear resultado ( evitar notacion cientifica si no es necesario )
            if isinstance(result, float) and result.is_integer():
                result_str = str(int(result))
            else:
                result_str = str(result)
            # mostrar
            self.display_var.set(result_str)
            # guardar en bd
            try:
                insert_calculation(expr, result_str)
            except Exception as db_e:
                messagebox.showwarning("bd", f"error guardando en bd: {db_e}")
            # Actualizar historial
            self._load_history()
        except Exception as e:
            messagebox.showerror("error", f"no se pudo evaluar la expresion :\n{e}")
    else:
        # añadir texto al display   
        cur = self.display_var.get()
        new = cur + label
        self.display_var.set(new)

def _load_history(self):
    try:
        rows = fetch_recent_calculations(limit=30)
        self.history_lb.delete(0, tk.END)
        for r in rows:
            _id, expr, result, created = r
            created_str = created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(created, datetime) else str(created)
            line = f"[{_id}] {created_str} — {expr} = {result}"
            self.history_lb.insert(tk.END, line)
    except Exception as e:
        # no bloquear la ui si no hay BD disponible ; mostrar mensaje y seguir .
        self.history_lb.delete(0, tk.END)
        self.history_lb.insert(tk.END, f"error cargando historial : {e}")

def _on_history_double_click(self, event):
    sel = self.history_lb.curselection()
    if not sel:
        return
    text = self.history_lb.get(sel[0])
    # extraer expresión (buscamos "— expr = result")
    try:
        # formato: "[id] fecha — expr = result" .
        parts = text.split("—", 1)
        if len(parts) >= 2:
            right = parts[1].strip()
            expr_part = right.rsplit("=", 1)[0].strip()
            self.display_var.set(expr_part)
    except Exception:
        pass

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()