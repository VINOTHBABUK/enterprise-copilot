import uuid
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.ingestion.database import Session, User
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY  = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM   = "HS256"
TOKEN_HOURS = 24


def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password.encode("utf-8"), salt
    ).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


def create_token(user):
    expire = datetime.utcnow() + timedelta(hours=TOKEN_HOURS)
    payload = {
        "sub":         user.email,
        "user_id":     user.id,
        "role":        user.role,
        "departments": user.departments,
        "name":        user.name,
        "exp":         expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def register_user(email, name, password, role="general",
                  departments=None):
    if departments is None:
        departments = ["general"]

    session = Session()

    existing = session.query(User)\
                      .filter_by(email=email).first()
    if existing:
        session.close()
        return None, "Email already registered"

    user = User(
        id            = str(uuid.uuid4()),
        email         = email,
        name          = name,
        password_hash = hash_password(password),
        role          = role,
        departments   = departments,
        is_active     = "true"
    )
    session.add(user)
    session.commit()
    session.close()
    return user, None


def login_user(email, password):
    session = Session()
    user    = session.query(User)\
                     .filter_by(email=email).first()

    if not user:
        session.close()
        return None, "User not found"

    if user.is_active != "true":
        session.close()
        return None, "Account deactivated"

    if not verify_password(password, user.password_hash):
        session.close()
        return None, "Invalid password"

    user.last_login = datetime.utcnow()
    session.commit()

    token = create_token(user)
    session.close()
    return token, None


def get_user_from_token(token):
    payload = decode_token(token)
    if not payload:
        return None
    return payload


def can_access_department(role, department):
    access_map = {
        "admin":       ["hr", "engineering",
                        "sales", "finance", "general"],
        "hr":          ["hr", "general"],
        "engineering": ["engineering", "general"],
        "sales":       ["sales", "general"],
        "finance":     ["finance", "general"],
        "general":     ["general"]
    }
    allowed = access_map.get(role, ["general"])
    return department in allowed


if __name__ == "__main__":
    print("Setting up initial users...\n")

    users = [
        {
            "email":       "admin@company.com",
            "name":        "Admin User",
            "password":    "Admin@123",
            "role":        "admin",
            "departments": ["hr", "engineering",
                            "sales", "finance", "general"]
        },
        {
            "email":       "hr@company.com",
            "name":        "HR Manager",
            "password":    "Hr@123",
            "role":        "hr",
            "departments": ["hr", "general"]
        },
        {
            "email":       "engineer@company.com",
            "name":        "Engineer",
            "password":    "Eng@123",
            "role":        "engineering",
            "departments": ["engineering", "general"]
        },
        {
            "email":       "sales@company.com",
            "name":        "Sales Rep",
            "password":    "Sales@123",
            "role":        "sales",
            "departments": ["sales", "general"]
        },
    ]

    for u in users:
        user, error = register_user(
            email       = u["email"],
            name        = u["name"],
            password    = u["password"],
            role        = u["role"],
            departments = u["departments"]
        )
        if error:
            print(f"  ✗ {u['email']}: {error}")
        else:
            print(f"  ✓ {u['email']} ({u['role']})")

    print("\nTesting login...")
    token, error = login_user("admin@company.com", "Admin@123")
    if token:
        print(f"  ✓ Login successful")
        payload = get_user_from_token(token)
        print(f"  ✓ Token decoded: {payload['name']} ({payload['role']})")
    else:
        print(f"  ✗ Login failed: {error}")
