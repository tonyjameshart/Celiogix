# path: dashboard_app.py
from app import App

if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
    finally:
        # Always close the SQLite connection when the window exits
        try:
            db = getattr(app, "db", None)
            if db is not None:
                db.close()
        except Exception:
            pass
