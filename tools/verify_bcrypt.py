"""Added to verify bcrypt hash/verify behavior."""

from getpass import getpass

# Import from auth module
from python_scripts.budget_planner.auth import (
    hash_password,
    verify_password,
)


def main() -> None:
    """Prompt for a password, hash it, and verify outcomes."""
    pwd = getpass("Enter a test password: ")
    hashed = hash_password(pwd)
    print("Hash (prefix):", hashed[:20] + "...")

    same_ok = verify_password(pwd, hashed)
    print("Verify same password:", same_ok)

    wrong_ok = verify_password("wrong-password", hashed)
    print("Verify wrong password:", wrong_ok)


if __name__ == "__main__":
    main()
