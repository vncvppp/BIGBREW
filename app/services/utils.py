"""
General utility helpers (password hashing, email sending, etc.).
"""

import hashlib
import random
import re
import smtplib
import string
from datetime import datetime
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import APP_CONFIG, EMAIL_CONFIG


class UtilityFunctions:
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hash."""
        return UtilityFunctions.hash_password(password) == hashed_password

    @staticmethod
    def generate_otp(length=6):
        """Generate numeric OTP."""
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def generate_reference_number(prefix="REQ"):
        """Generate unique reference number."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}{timestamp}{random_str}"

    @staticmethod
    def is_valid_email(email):
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None


class EmailService:
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = EMAIL_CONFIG.get("smtp_port", 587)
        self.email_address = EMAIL_CONFIG.get("email_address", "")
        self.email_password = EMAIL_CONFIG.get("email_password", "")
        self.email_enabled = bool(self.email_address and self.email_password)

        if self.email_enabled:
            print(f"✓ Email service configured for: {self.email_address}")
        else:
            print("⚠️ Email service disabled - configure EMAIL_ADDRESS and EMAIL_PASSWORD in .env")

    def send_otp_email(self, to_email, otp_code):
        """Send OTP email using real SMTP."""
        try:
            if not self.email_enabled:
                return self._fallback_otp_email(to_email, otp_code, "SIMULATION")

            subject = "BigBrew Coffee Shop - Customer Account Verification"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <div style="text-align: center; background: #8B4513; padding: 20px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: #DAA520; margin: 0;">BIGBREW COFFEE SHOP</h1>
                        <h2 style="color: white; margin: 10px 0 0 0;">POS Management System</h2>
                    </div>

                    <div style="padding: 30px;">
                        <h2 style="color: #8B4513;">OTP Verification Code</h2>
                        <p>Dear Valued Customer,</p>
                        <p>Welcome to BigBrew Coffee Shop! Your One-Time Password (OTP) for account verification is:</p>

                        <div style="text-align: center; margin: 30px 0;">
                            <span style="font-size: 32px; font-weight: bold; color: #8B4513;
                                       background: #FFF8DC; padding: 15px 30px;
                                       border-radius: 5px; letter-spacing: 5px; border: 2px solid #DAA520;">
                                {otp_code}
                            </span>
                        </div>

                        <p><strong>This OTP will expire in 3 minutes.</strong></p>
                        <p>After verification, you'll have access to your BigBrew customer account with loyalty rewards and online ordering.</p>
                        <p>If you did not request this verification, please contact our support team immediately.</p>

                        <hr style="margin: 30px 0; border-color: #DAA520;">
                        <p style="color: #8B4513; font-size: 12px; text-align: center;">
                            <strong>BigBrew Coffee Shop</strong><br>
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            success = self._send_email(to_email, subject, body)

            if success:
                print(f"✓ OTP email sent to: {to_email}")
                return True

            print("⚠️ Failed to send OTP email, using fallback")
            return self._fallback_otp_email(to_email, otp_code, "FALLBACK")

        except Exception as exc:
            print(f"❌ Email error: {exc}")
            return self._fallback_otp_email(to_email, otp_code, "FALLBACK")

    def _send_email(self, to_email, subject, body):
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart()
            msg["From"] = f"BigBrew Coffee Shop <{self.email_address}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as exc:
            print(f"❌ SMTP error: {exc}")
            return False
        except Exception as exc:
            print(f"❌ Email sending error: {exc}")
            return False

    def send_email_with_attachments(self, to_email, subject, body, attachments_data):
        """Send email with attachments from database BLOB data."""
        try:
            if not self.email_enabled:
                return self._fallback_attachment_email(to_email, subject, body, attachments_data)

            msg = MIMEMultipart()
            msg["From"] = f"BigBrew Coffee Shop <{self.email_address}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html"))

            for attachment in attachments_data:
                file_name = attachment["file_name"]
                file_data = attachment["file_data"]  # BLOB from database
                file_type = attachment.get("file_type", "application/pdf")

                if file_data:
                    maintype, subtype = (
                        file_type.split("/", 1) if "/" in file_type else ("application", "octet-stream")
                    )

                    part = MIMEBase(maintype, subtype)
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f'attachment; filename="{file_name}"')
                    msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            print(f"✓ Email with attachments sent to: {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as exc:
            print(f"❌ SMTP error: {exc}")
            return self._fallback_attachment_email(to_email, subject, body, attachments_data)
        except Exception as exc:
            print(f"❌ Email with attachments error: {exc}")
            return self._fallback_attachment_email(to_email, subject, body, attachments_data)

    def _fallback_otp_email(self, to_email, otp_code, mode="SIMULATION"):
        """Fallback method for OTP email."""
        print("=" * 50)
        print(f"📧 OTP EMAIL ({mode})")
        print("=" * 50)
        print(f"To: {to_email}")
        print("Subject: BigBrew Coffee Shop - Customer Account Verification")
        print(f"OTP Code: {otp_code}")
        print("=" * 50)
        if mode == "SIMULATION":
            print("In production, this would be sent via real email")
        else:
            print("Email service unavailable - using fallback")
        print("=" * 50)
        return True

    def _fallback_confirmation_email(self, to_email, request_details):
        """Fallback for confirmation email."""
        print("=" * 50)
        print("📧 ORDER CONFIRMATION SIMULATION")
        print("=" * 50)
        print(f"To: {to_email}")
        print(f"Order: {request_details.get('order_name', 'N/A')}")
        print(f"Reference: {request_details.get('reference_number', 'N/A')}")
        print("=" * 50)
        return True

    def _fallback_attachment_email(self, to_email, subject, body, attachments_data):
        """Fallback for email with attachments."""
        print("=" * 60)
        print("📧 EMAIL WITH ATTACHMENTS (FALLBACK)")
        print("=" * 60)
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Attachments: {[att['file_name'] for att in attachments_data]}")
        print(f"Body: {body[:100]}...")
        print("=" * 60)
        print("✅ Email with attachments would be sent to", to_email)
        print("=" * 60)
        return True


class PaymentProcessor:
    @staticmethod
    def process_online_payment(amount, payment_method, reference_number):
        """Simulate payment processing."""
        print(f"💳 Processing payment: {amount} via {payment_method} - Ref: {reference_number}")

        return {
            "success": True,
            "transaction_id": f"TXN{reference_number}",
            "message": "Payment processed successfully (Simulation Mode)",
        }


# Global utility instances
email_service = EmailService()
payment_processor = PaymentProcessor()


