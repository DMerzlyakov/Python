import yaml


class DataHelp:

    def __init__(self):
        self.path = "./data/users.yml"
        self.data = []
        self.read_data()

    def read_data(self):
        with open(self.path, "r") as f:
            data = yaml.safe_load(f)
            if data is None:
                data = []
            self.data = data

    def authorization(self, ip, password):

        for user in self.data:
            if user["ip"] == ip and user["password"] == password:
                return 1, user["username"]

        for user in self.data:
            if user["ip"] == ip:
                return 0, None

        return -1, None

    def user_reg(self, ip, password, username):
        self.data.append({"ip": ip, "password": password, "username": username})
        with open(self.path, "w") as f:
            yaml.dump(self.data, f)
