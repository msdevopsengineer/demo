import pyotp
import qrcode
import io
import base64
from app.core.config import settings

class TOTPService:
    def generate_secret(self) -> str:
        """Generate a random Base32 secret"""
        return pyotp.random_base32()

    def get_totp_uri(self, secret: str, user_email: str, issuer: str = "CustomAuthenticator") -> str:
        return pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name=issuer)

    def generate_qr_code(self, uri: str) -> str:
        """Generate SVG QR code and return as string"""
        img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage)
        stream = io.BytesIO()
        img.save(stream)
        return stream.getvalue().decode()

    def verify_code(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verify TOTP code.
        valid_window: 1 means accept code for current time +/- 30 seconds.
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)

totp_service = TOTPService()
