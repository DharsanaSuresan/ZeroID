import random
import string

def generate_users(n):
    users = []
    for i in range(n):
        name = ''.join(random.choices(string.ascii_letters, k=8))
        users.append(name + str(i))
    return users
