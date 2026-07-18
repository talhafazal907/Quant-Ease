import bcrypt

class Hash:
    """ This class is Responsible for the hashing of user passwords""" 
    def __init__(self):
        pass

    def create_hash(self, password : str):
        encoded_pass = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(encoded_pass, salt)

        return hash
    
    def match(self, password : str, hash : str):
        encoded_pass = password.encode("utf-8")
        encoded_hash = hash.encode("utf-8")
        if bcrypt.checkpw(encoded_pass, encoded_hash):
            return 1
        else: 
            None
    