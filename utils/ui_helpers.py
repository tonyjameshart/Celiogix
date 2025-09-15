from tkinter import ttk

def create_treeview(parent, columns, col_defs, **kwargs):
    tv = ttk.Treeview(parent, columns=columns, show="headings", **kwargs)
    for k, h, w, a in col_defs:
        tv.heading(k, text=h)
        anc = {"w": "w", "c": "center", "e": "e"}.get(a, "w")
        tv.column(k, width=w, anchor=anc, stretch=True)
    return tv