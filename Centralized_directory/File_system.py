class File_system:
    def __init__(self, md5, filename):
        self.md5 = md5
        self.filename = filename

    def write(self):
        file = open("File_System.txt","a")

        content = self.md5 + "|" + self.filename
        file.write(content)

        file.close()

    def read(self):
        f = open("File_System.txt", "r")
        contents = f.readlines()

        for content in contents:
            content.split("|")
            dict[content[0]] = content[1]

        f.close()

        return dict