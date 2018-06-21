class log_file(object):
    def __init__(self, name_file):
        self.name_file = name_file
        self.dict = {}
        self.token = ": "

    def add_arg(self, key, value):
        if type(key) == str and type(value) in [int, str, float, list, tuple]:
            self.dict[key] = value
        elif type(key) == list and type(value) == list and len(key) == len(value):
            self.dict.update(dict(zip(key, value)))

    def set_arg(self, key, value):
        if type(key) == str and type(value) in [int, str, float, list, tuple]:
            self.dict[key] = value
        elif type(key) == list and type(value) == list and len(key) == len(value):
            self.dict.update(dict(zip(key, value)))

    def __str__(self):
        string = ""
        for i, j in self.dict.items():
            if type(j) != list:
                string += "%s%s%s\n" % (i, self.token, j)
        return string

    def carregar(self):
        with open(self.name_file, "r") as file:
            reading = file.read()
            lines = reading.split("\n")
            keys = []
            for i in lines:
                if len(i.split(self.token)) > 1:
                    keys.append(i.split(self.token)[0])
            for i in range(len(keys)-1):
                x = reading.split(keys[i+1])
                value = x[0].replace(keys[i]+self.token, "")
                self.dict[keys[i]] = value[1:-1].split("\n") if value.count(
                    "\n") > 1 else value.replace("\n", "")
                reading = reading.replace(x[0], "")

            value = reading.split(keys[-1]+self.token)
            self.dict[keys[-1]] = value[-1][1:-1].split("\n")

    def salvar(self):
        with open(self.name_file, "w") as file:
            for key, values in self.dict.items():
                if type(values) in [int, str, float]:
                    file.write("%s: %s\n" % (key, str(values)))
            for key, values in self.dict.items():
                if type(values) in [list, tuple]:
                    file.write("%s: \n" % (key))
                    for i in values:
                        file.write("%s\n" % str(i))


'''
file_name = "LOG_teste.txt"
lg = log_file(file_name)

lg.add_arg("path superv", "PATH")
lg.add_arg("path backup", "BACKUP")
lg.add_arg("data", "DATA")
lg.add_arg("Files", [1,2,3,4])
lg.add_arg("Dirs", (5,1,9,8))

#lg.salvar()
lg.carregar()
print(lg)
'''
