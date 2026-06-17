import json
import os
import fcntl

USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "users.json"
)


def add_tokens(username: str, amount: int) -> int | None:
    if not os.path.exists(USERS_FILE):
        return None
    with open(USERS_FILE, "r+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        users = json.load(f)
        if username not in users:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return None
        users[username]["tokens"] = users[username].get("tokens", 0) + amount
        new_balance = users[username]["tokens"]
        f.seek(0)
        f.truncate()
        json.dump(users, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return new_balance


def unlock_with_cost(username: str, unlock_id: str, cost: int = 1) -> tuple[bool, int]:
    if not os.path.exists(USERS_FILE):
        return False, 0
    with open(USERS_FILE, "r+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        users = json.load(f)
        if username not in users:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return False, 0

        user = users[username]
        user.setdefault("unlocked", [])
        balance = user.get("tokens", 0)

        if unlock_id in user["unlocked"]:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return True, balance
        if balance < cost:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return False, balance

        user["tokens"] = balance - cost
        user["unlocked"].append(unlock_id)
        new_balance = user["tokens"]
        f.seek(0)
        f.truncate()
        json.dump(users, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return True, new_balance
