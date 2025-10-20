"""
Password hashing and verification service using bcrypt.

Security Best Practices:
- Uses bcrypt for password hashing (industry standard)
- Automatic salt generation
- Configurable work factor (cost)
- Constant-time password verification
"""

import bcrypt
from typing import Optional


class PasswordService:
    """Service for secure password hashing and verification."""

    def __init__(self, cost_factor: int = 12):
        """
        Initialize password service.

        Args:
            cost_factor: bcrypt work factor (4-31, default: 12)
                        Higher = more secure but slower
                        12 = recommended for production
        """
        self.cost_factor = cost_factor

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string (bcrypt format)

        Example:
            >>> service = PasswordService()
            >>> hashed = service.hash_password("mypassword123")
            >>> print(hashed)  # $2b$12$...
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')

        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=self.cost_factor)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            password_hash: Stored bcrypt hash

        Returns:
            True if password matches, False otherwise

        Example:
            >>> service = PasswordService()
            >>> hashed = service.hash_password("mypassword123")
            >>> service.verify_password("mypassword123", hashed)  # True
            >>> service.verify_password("wrongpassword", hashed)   # False
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')

            # Constant-time comparison
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            # Invalid hash or other error
            return False

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> PasswordService.validate_password_strength("Pass123!")
            (True, None)
            >>> PasswordService.validate_password_strength("weak")
            (False, "Password must be at least 8 characters long")
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character (!@#$%^&* etc.)"

        return True, None


# Singleton instance
password_service = PasswordService()
