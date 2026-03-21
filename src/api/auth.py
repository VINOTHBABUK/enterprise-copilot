from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

USERS = {
    "hr_user": {
        "password":    "hr123",
        "role":        "hr",
        "departments": ["hr", "general"],
        "name":        "HR Manager"
    },
    "eng_user": {
        "password":    "eng123",
        "role":        "engineering",
        "departments": ["engineering", "general"],
        "name":        "Engineer"
    },
    "admin_user": {
        "password":    "admin123",
        "role":        "admin",
        "departments": ["hr", "engineering",
                        "sales", "finance", "general"],
        "name":        "Admin"
    },
    "sales_user": {
        "password":    "sales123",
        "role":        "sales",
        "departments": ["sales", "general"],
        "name":        "Sales Rep"
    }
}


def authenticate(username, password):
    user = USERS.get(username)
    if not user:
        return None
    if user["password"] != password:
        return None
    return {
        "username":    username,
        "role":        user["role"],
        "departments": user["departments"],
        "name":        user["name"]
    }


def get_allowed_departments(role):
    for user in USERS.values():
        if user["role"] == role:
            return user["departments"]
    return ["general"]


def can_access_department(role, department):
    allowed = get_allowed_departments(role)
    return department in allowed


if __name__ == "__main__":
    print("Testing RBAC...\n")

    test_cases = [
        ("hr_user",    "hr123",    "hr"),
        ("eng_user",   "eng123",   "engineering"),
        ("hr_user",    "hr123",    "engineering"),
        ("admin_user", "admin123", "finance"),
        ("hr_user",    "wrongpwd", "hr"),
    ]

    for username, password, dept in test_cases:
        user = authenticate(username, password)
        if user:
            access = can_access_department(
                user["role"], dept
            )
            status = "✓ allowed" if access else "✗ denied"
            print(f"{username} → {dept}: {status}")
        else:
            print(f"{username} → login failed") 