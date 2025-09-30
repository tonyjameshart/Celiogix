from tkinter import ttk


def create_treeview(parent, columns, col_defs, **kwargs):
    tv = ttk.Treeview(parent, columns=columns, show="headings", **kwargs)
    # tv is your Treeview, wrap is its container frame
    for c in tv.cget("columns"):
        tv.column(c, stretch=False)

    wrap.update_idletasks()
    wrap.configure(width=wrap.winfo_reqwidth(), height=wrap.winfo_reqheight())
    wrap.grid_propagate(False)

    # make sure the grid cell isn't resizable and the widget isn’t sticky everywhere
    info = wrap.grid_info()
    parent = wrap.master
    parent.grid_rowconfigure(int(info.get("row", 0)), weight=0)
    parent.grid_columnconfigure(int(info.get("column", 0)), weight=0)
    wrap.grid(sticky="nw")

    return tv
