from werkzeug.security import safe_str_cmp # for safer strings comparison
from user import User

# users = [
#     User(1, "Enver", "qwerty")
# ]

# username_mapping = { u.username: u for u in users } # assigning key:value pairs
# userid_mapping = { u.id: u for u in users }

def authenticate(username, password):
    user = User.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        return user

def identity(payload): # payload - contents of the JWT token
    user_id = payload['identity']
    return User.find_by_id(user_id)
