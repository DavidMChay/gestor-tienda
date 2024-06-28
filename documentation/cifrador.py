from werkzeug.security import generate_password_hash

print("Welcome to the password hasher")
print("Please enter the password you want to hash")
password = input()
hashed_password = generate_password_hash(password)
print(hashed_password)
