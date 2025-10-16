import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from tkinter import Canvas, Entry, Button, PhotoImage
import hashlib
import bcrypt
from db_config import db
from dashboard import DashboardManager


class LoginModule:
    def __init__(self):
        # Window setup per new Tkinter Designer layout
        self.root = tk.Tk()
        self.root.title("BigBrew - Login")
        self.root.geometry("800x440")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)

        # Assets path from provided layout
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = self.OUTPUT_PATH / Path(r"C:\Users\Admin\Downloads\Output_design\build\assets\frame0")

        def relative_to_assets(path: str) -> Path:
            return self.ASSETS_PATH / Path(path)

        # Canvas and background image
        self.canvas = Canvas(
            self.root,
            bg="#FFFFFF",
            height=440,
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        try:
            self.image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
            self.canvas.create_image(400.0, 220.0, image=self.image_image_1)
        except Exception:
            # If assets are missing, continue without background image
            pass

        # Login button
        try:
            self.button_image_login = PhotoImage(file=relative_to_assets("button_login.png"))
            self.button_login = Button(
                image=self.button_image_login,
                borderwidth=0,
                highlightthickness=0,
                command=self.handle_login,
                relief="flat"
            )
        except Exception:
            self.button_login = Button(
                text="Login",
                borderwidth=0,
                highlightthickness=0,
                command=self.handle_login,
                relief="flat",
                bg="#D2691E",
                fg="#FFFFFF"
            )
        self.button_login.place(x=54.0, y=323.0, width=245.0, height=42.0)

        # Password entry (from layout)
        try:
            self.entry_image_pass = PhotoImage(file=relative_to_assets("entry_pass.png"))
            self.canvas.create_image(177.5, 240.0, image=self.entry_image_pass)
        except Exception:
            pass
        self.password_entry = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#000716",
            highlightthickness=0,
            show="*"
        )
        self.password_entry.place(x=63.0, y=220.0, width=229.0, height=38.0)

        # Username entry (from layout)
        try:
            self.entry_image_username = PhotoImage(file=relative_to_assets("entry_username.png"))
            self.canvas.create_image(176.5, 188.0, image=self.entry_image_username)
        except Exception:
            pass
        self.username_entry = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#000716",
            highlightthickness=0
        )
        self.username_entry.place(x=62.0, y=168.0, width=229.0, height=38.0)

        # Eye toggle button
        self.show_password = False
        try:
            self.button_image_eye = PhotoImage(file=relative_to_assets("button_eye.png"))
            self.button_eye = Button(
                image=self.button_image_eye,
                borderwidth=0,
                highlightthickness=0,
                command=self.toggle_password_visibility,
                relief="flat"
            )
        except Exception:
            self.button_eye = Button(
                text="👁",
                borderwidth=0,
                highlightthickness=0,
                command=self.toggle_password_visibility,
                relief="flat"
            )
        self.button_eye.place(x=272.0, y=230.0, width=20.0, height=19.0)

        # Optional other buttons (no-op placeholders wired for future)
        try:
            self.button_image_forgot = PhotoImage(file=relative_to_assets("button_forgotpass.png"))
            Button(
                image=self.button_image_forgot,
                borderwidth=0,
                highlightthickness=0,
                command=self.on_forgot_password,
                relief="flat"
            ).place(x=194.0, y=272.0, width=106.0, height=15.0)
        except Exception:
            pass

        try:
            self.button_image_signup = PhotoImage(file=relative_to_assets("button_signup.png"))
            Button(
                image=self.button_image_signup,
                borderwidth=0,
                highlightthickness=0,
                command=self.on_signup,
                relief="flat"
            ).place(x=100.0, y=377.0, width=158.0, height=18.0)
        except Exception:
            pass

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        self.password_entry.config(show="" if self.show_password else "*")

    def on_forgot_password(self):
        messagebox.showinfo("Forgot Password", "Please contact your administrator to reset your password.")

    def on_signup(self):
        messagebox.showinfo("Sign Up", "Account creation is managed by administrators.")

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        user = self.authenticate_user(username, password)
        if user:
            db.update_last_login(user['user_id'])
            self.root.withdraw()
            DashboardManager(user, self.root).show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password, or account inactive")

    def authenticate_user(self, username, password):
        try:
            user = db.get_user_by_username(username)
            if not user:
                return None
            if not user['is_active']:
                messagebox.showerror("Account Inactive", "Your account has been deactivated")
                return None

            entered_bytes = password.encode('utf-8')
            stored = (user['password_hash'] or '').strip()

            # Determine if the stored hash is bcrypt
            is_bcrypt = stored.startswith("$2a$") or stored.startswith("$2b$") or stored.startswith("$2y$")

            if is_bcrypt:
                try:
                    if bcrypt.checkpw(entered_bytes, stored.encode('utf-8')):
                        return user
                    return None
                except ValueError as e:
                    # Covers malformed bcrypt strings (e.g., "Invalid salt")
                    messagebox.showerror("Database Error", f"Stored password hash is invalid: {str(e)}")
                    return None
            else:
                # Non-bcrypt path: support legacy SHA2(256) hex or plaintext
                sha256_hex = hashlib.sha256(entered_bytes).hexdigest()

                if stored.lower() == sha256_hex.lower() or stored == password:
                    # Auto-upgrade to bcrypt
                    try:
                        new_hash = bcrypt.hashpw(entered_bytes, bcrypt.gensalt()).decode('utf-8')
                        db.update_password_hash(user['user_id'], new_hash)
                    except Exception:
                        pass
                    return user
                return None
        except Exception as e:
            messagebox.showerror("Database Error", f"Unable to connect to database: {str(e)}")
            return None

    def run(self):
        if not db.test_connection():
            messagebox.showerror("Database Error", "Unable to connect to database. Please check your MySQL server.")
            return
        self.root.mainloop()


if __name__ == "__main__":
    app = LoginModule()
    app.run()
