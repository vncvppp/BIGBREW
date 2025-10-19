from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, messagebox
import mysql.connector
from utils import UtilityFunctions, EmailService
from otp import OTPVerificationWindow
import sys
import os
import re
from datetime import datetime

OUTPUT_PATH = Path(__file__).parent

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def relative_to_assets(path: str) -> Path:
    """Get path to assets in the signup resources folder"""
    possible_paths = [
        resource_path(f"resources/signup/{path}"),
        resource_path(f"signup/resources/{path}"),
        os.path.join(OUTPUT_PATH, "resources", "signup", path),
        os.path.join(OUTPUT_PATH, "signup", "resources", path),
        resource_path(path),
    ]
    
    for asset_path in possible_paths:
        if os.path.exists(asset_path):
            return Path(asset_path)
    
    # If no path found, return the most likely one
    return Path(possible_paths[0])

class SignupWindow:
    def __init__(self, parent, show_login_callback, get_db_connection):
        self.parent = parent
        self.show_login_callback = show_login_callback
        self.get_db_connection = get_db_connection
        self.otp_code = None
        self.user_data = None
        self.images = []  # Keep references to images
        
        # Placeholder texts
        self.email_placeholder = "example@gmail.com"
        self.studentno_placeholder = "PDM-2025-001234"
        
        # Load eye images for toggle
        self.button_hidden_img = self.load_image("button_eye.png")   
        self.button_view_img = self.load_image("button_eye.png")
        
        self.setup_ui()
        
    def load_image(self, path: str):
        """Load image and keep reference to prevent garbage collection"""
        try:
            image_path = relative_to_assets(path)
            if not image_path.exists():
                print(f"Image not found: {image_path}")
                return None
            photo_image = PhotoImage(file=image_path)
            self.images.append(photo_image)
            return photo_image
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
        
    def setup_ui(self):
        """Setup the signup UI"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Create canvas
        self.canvas = Canvas(
            self.parent,
            bg="#FFFFFF",
            height=440,
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        # Load background image
        image_image_1 = self.load_image("image_1.png")
        if image_image_1:
            self.canvas.create_image(400.0, 220.0, image=image_image_1)

        # Password entry
        entry_image_pass = self.load_image("entry_pass.png")
        if entry_image_pass:
            self.canvas.create_image(177.5, 240.0, image=entry_image_pass)
            
        self.entry_pass = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#000716",
            highlightthickness=0,
            show='*',
            font=("Inter", 12)
        )
        self.entry_pass.place(x=63.0, y=220.0, width=229.0, height=38.0)

        # Email entry
        entry_image_email = self.load_image("entry_email.png")
        if entry_image_email:
            self.canvas.create_image(176.5, 188.0, image=entry_image_email)
            
        self.entry_email = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#666666",
            highlightthickness=0,
            font=("Inter", 12)
        )
        self.entry_email.place(x=62.0, y=168.0, width=229.0, height=38.0)
        self.entry_email.insert(0, self.email_placeholder)
        self.entry_email.bind('<FocusIn>', lambda e: self.clear_placeholder(self.entry_email, self.email_placeholder))
        self.entry_email.bind('<FocusOut>', lambda e: self.restore_placeholder(self.entry_email, self.email_placeholder))

        # Confirm password entry
        entry_image_confirmpass = self.load_image("entry_confirmpass.png")
        if entry_image_confirmpass:
            self.canvas.create_image(178.5, 291.0, image=entry_image_confirmpass)
            
        self.entry_confirmpass = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#000716",
            highlightthickness=0,
            show='*',
            font=("Inter", 12)
        )
        self.entry_confirmpass.place(x=64.0, y=271.0, width=229.0, height=38.0)

        def toggle_entry_password(target_entry):
            """Toggle password visibility for target entry"""
            current = target_entry.cget('show')
            target_entry.config(show='' if current == '*' else '*')

        # Password visibility toggle
        button_image_eye_pass = self.load_image("button_eye.png")
        if button_image_eye_pass:
            button_eye_pass = Button(
                image=button_image_eye_pass,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: toggle_entry_password(self.entry_pass),
                relief="flat",
                cursor="hand2"
            )
        else:
            button_eye_pass = Button(
                text="👁",
                borderwidth=0,
                highlightthickness=0,
                command=lambda: toggle_entry_password(self.entry_pass),
                relief="flat",
                cursor="hand2"
            )
        button_eye_pass.place(x=272.0, y=230.0, width=20.0, height=19.0)

        # Confirm password visibility toggle
        button_image_eye_confirm = self.load_image("button_eye.png")
        if button_image_eye_confirm:
            button_eye_confirm = Button(
                image=button_image_eye_confirm,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: toggle_entry_password(self.entry_confirmpass),
                relief="flat",
                cursor="hand2"
            )
        else:
            button_eye_confirm = Button(
                text="👁",
                borderwidth=0,
                highlightthickness=0,
                command=lambda: toggle_entry_password(self.entry_confirmpass),
                relief="flat",
                cursor="hand2"
            )
        button_eye_confirm.place(x=272.0, y=283.0, width=20.0, height=19.0)

        # Title
        self.canvas.create_rectangle(
            110.0, 124.0, 247.0, 140.0,
            fill="#3A280F", outline=""
        )

        # Login button
        button_image_login = self.load_image("button_login.png")
        if button_image_login:
            button_login = Button(
                image=button_image_login,
                borderwidth=0,
                highlightthickness=0,
                command=self.show_login_callback,
                relief="flat",
                cursor="hand2"
            )
        else:
            button_login = Button(
                text="Back to Login",
                borderwidth=0,
                highlightthickness=0,
                command=self.show_login_callback,
                relief="flat",
                bg="#D2691E",
                fg="#FFFFFF",
                cursor="hand2"
            )
        button_login.place(x=70.0, y=376.0, width=204.0, height=26.0)

        # Signup button
        button_image_signup = self.load_image("button_signup.png")
        if button_image_signup:
            button_signup = Button(
                image=button_image_signup,
                borderwidth=0,
                highlightthickness=0,
                command=self.attempt_signup,
                relief="flat",
                cursor="hand2"
            )
        else:
            button_signup = Button(
                text="Sign Up",
                borderwidth=0,
                highlightthickness=0,
                command=self.attempt_signup,
                relief="flat",
                bg="#3A280F",
                fg="#FFFFFF",
                cursor="hand2"
            )
        button_signup.place(x=54.0, y=323.0, width=245.0, height=42.0)

        # Set focus to email entry
        self.entry_email.focus()

    def clear_placeholder(self, entry, placeholder_text):
        """Clear placeholder text when entry is focused"""
        if entry.get() == placeholder_text:
            entry.delete(0, 'end')
            entry.config(fg="#000716")
            if entry == self.entry_pass:
                entry.config(show="*")

    def restore_placeholder(self, entry, placeholder_text):
        """Restore placeholder text when entry loses focus and is empty"""
        if entry.get().strip() == "":
            entry.insert(0, placeholder_text)
            entry.config(fg="#666666")
            if entry == self.entry_pass:
                entry.config(show="")

    def is_valid_pdm_student_number(self, student_number):
        """Validate PDM student number format: PDM-YYYY-NNNNNN"""
        pattern = r'^PDM-\d{4}-\d{6}$'
        return re.match(pattern, student_number.upper()) is not None
    
    def force_uppercase_and_validate(self, event=None):
        """Force uppercase and run validation"""
        current_text = self.entry_studentno.get()
        upper_text = current_text.upper()

        if current_text != upper_text:
            cursor_pos = self.entry_studentno.index("insert")
            self.entry_studentno.delete(0, "end")
            self.entry_studentno.insert(0, upper_text)
            try:
                self.entry_studentno.icursor(cursor_pos)
            except:
                self.entry_studentno.icursor("end")

        self.validate_student_number_format()

    def validate_student_number_format(self, event=None):
        """Validate student number format in real-time"""
        student_number = self.entry_studentno.get().strip()

        if student_number == self.studentno_placeholder:
            return

        if len(student_number) > 0:
            student_number = student_number.upper()
            cleaned = re.sub(r'[^A-Z0-9-]', '', student_number)
            raw = cleaned.replace("-", "")

            if raw.startswith("PDM") and len(raw) > 3:
                year_part = raw[3:7] if len(raw) > 7 else raw[3:]
                number_part = raw[7:13] if len(raw) > 7 else ""

                formatted = f"PDM-{year_part}"

                if cleaned.endswith("-") and not number_part:
                    formatted += "-"
                elif number_part:
                    formatted += f"-{number_part}"

                if formatted != cleaned:
                    current_pos = self.entry_studentno.index('insert')
                    self.entry_studentno.delete(0, 'end')
                    self.entry_studentno.insert(0, formatted)

                    try:
                        self.entry_studentno.icursor(min(current_pos, len(formatted)))
                    except:
                        self.entry_studentno.icursor('end')

            if student_number and student_number != self.studentno_placeholder:
                if self.is_valid_pdm_student_number(student_number):
                    self.entry_studentno.config(fg="#006400")
                else:
                    self.entry_studentno.config(fg="#8B0000")

    def attempt_signup(self):
        """Attempt to sign up the user"""
        email = self.entry_email.get().strip()
        password = self.entry_pass.get().strip()
        confirm_password = self.entry_confirmpass.get().strip()

        # Remove placeholder values if they weren't changed
        if email == self.email_placeholder:
            email = ""

        # Validation
        if not all([email, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            if not email:
                self.restore_placeholder(self.entry_email, self.email_placeholder)
            return

        if not UtilityFunctions.is_valid_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            self.entry_email.focus()
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            self.entry_pass.focus()
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            self.entry_pass.focus()
            return

        db_connection = self.get_db_connection()
        if not db_connection:
            messagebox.showerror("Database Error", "Cannot connect to database")
            return

        try:
            cursor = db_connection.cursor(dictionary=True)

            # Check if email already exists in users table
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Email already registered")
                return

            # Generate OTP and store temporary user data
            self.otp_code = UtilityFunctions.generate_otp()
            self.user_data = {
                'email': email,
                'password': password,
                'username': email.split('@')[0]  # Use email prefix as username
            }

            # Send OTP email
            email_service = EmailService()
            if email_service.send_otp_email(email, self.otp_code):
                self.show_otp_verification()
            else:
                messagebox.showerror("Error", "Failed to send OTP. Please try again.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Registration failed: {str(e)}")
        finally:
            if db_connection and db_connection.is_connected():
                cursor.close()

    def show_otp_verification(self):
        """Show OTP verification window"""
        self.destroy()
        OTPVerificationWindow(
            self.parent, 
            self.user_data, 
            self.otp_code, 
            self.complete_registration,
            self.show_login_callback,
            self.get_db_connection
        )

    def complete_registration(self):
        """Complete the registration process with proper transaction handling"""
        db_connection = self.get_db_connection()
        if not db_connection or not self.user_data:
            messagebox.showerror("Error", "Registration failed")
            return

        cursor = None
        try:
            cursor = db_connection.cursor(dictionary=True)
            
            # Check for active transaction and rollback if needed
            try:
                if db_connection.in_transaction:
                    db_connection.rollback()
            except:
                pass
            
            # Hash password
            hashed_password = UtilityFunctions.hash_password(self.user_data['password'])
            
            # Start fresh transaction
            db_connection.start_transaction()
            
            # Insert into users table (authentication)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, user_type, is_active) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.user_data['username'],
                self.user_data['email'],
                hashed_password,
                'cashier',  # Default user type for BigBrew POS
                True
            ))
            
            user_id = cursor.lastrowid
            
            db_connection.commit()
            
            # Show success message
            success_message = f"""
            Registration completed successfully!

            Account Information:
            • Username: {self.user_data['username']}
            • Email: {self.user_data['email']}
            • User Type: Cashier

            You can now login using your username or email.
            """
            
            messagebox.showinfo("Success", success_message.strip())
            self.show_login_callback()
            
        except mysql.connector.Error as e:
            try:
                db_connection.rollback()
            except:
                pass
            
            error_message = f"Registration failed: {str(e)}"
            if "Duplicate entry" in str(e):
                if "email" in str(e):
                    error_message = "Email already registered. Please use a different email address."
                elif "username" in str(e):
                    error_message = "Username already taken. Please choose a different username."
            
            messagebox.showerror("Registration Error", error_message)
            
        except Exception as e:
            try:
                db_connection.rollback()
            except:
                pass
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")
            
        finally:
            if cursor:
                cursor.close()
            
    def destroy(self):
        """Clean up the window"""
        for widget in self.parent.winfo_children():
            widget.destroy()

# For testing purposes - can be removed when integrated
if __name__ == "__main__":
    def test_show_login():
        print("Would show login window")
    
    def test_get_db_connection():
        from db_config import db
        return db.get_connection()
    
    window = Tk()
    window.geometry("800x440")
    window.configure(bg="#FFFFFF")
    window.resizable(False, False)
    
    signup_window = SignupWindow(
        window, 
        test_show_login, 
        test_get_db_connection
    )
    
    window.mainloop()