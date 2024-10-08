import re


# Make a regular expression
# for validating an Email
email_pattern = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"


err_message = "DETAIL:.+\."

pwdstr = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[\]\:\;\<\>\,.?\/\~\_+\-\=|]).{8,32}$"


def check_email(email: str):
    """[https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/]"""
    # pass the regular expression
    # and the string in search() method

    if email and (re.search(email_pattern, email)):
        return True
    else:
        print("Invalid Email")
        return False


def errmsn(message: str):
    data = re.findall(err_message, message)
    print(data)
    if data:
        return data[0]


def pwd(password: str):
    return re.match(pwdstr, password)
