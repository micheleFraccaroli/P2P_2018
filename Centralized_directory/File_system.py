class File_system:
    def __init__(self, md5, filename):
        self.md5 = md5
        self.filename = filename

    def write(self):
        file = open("File_System.txt","a")

        content = self.md5 + "|" + self.filename + "\n"
        file.write(content)

        file.close()

    def read(self):
        dict = {}
        f = open("File_System.txt", "r")
        
        r = f.read().splitlines()
        for i in r:
            line = i.split("|")
            dict[line[0]] = line[1]

        f.close()

        return dict

    def over(self, dict):
        f = open("File_System.txt","w")

        for i in dict:
            line = i + "|" + dict[i] + "\n"
            f.write(line)

        f.close()

        return dict