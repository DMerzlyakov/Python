import os
import pathlib
import shutil
from settings import *


class CommandHandler:

    def __init__(self):
        self.sep = os.sep
        self.way = Paths(self.sep)

    def cd(self, filename):
        self.way.add_path(filename)
        current_path = self.way.path

        try:
            os.chdir(current_path)
        except FileNotFoundError:
            self.way.add_path(f"..{self.sep}")
            print("Данной директории не существует")
        except NotADirectoryError:
            self.way.add_path(f"..{self.sep}")
            print("Файл не может являться дерикторией ")

    def ls(self):
        current_path = self.way.path
        files = os.listdir(current_path)
        for i in range(len(files)):
            if os.path.isdir(self.way.path_to_file(files[i])):
                files[i] = f"|dir| {files[i]}"
            elif os.path.isfile(self.way.path_to_file(files[i])):
                files[i] = f"|file| {files[i]}"

        result = "\n".join(files)
        print(f"Содержимое {current_path}:\n{result}")

    def mkdir(self, filename):
        current_path = self.way.path_to_file(filename)
        try:
            os.mkdir(current_path)
        except FileExistsError:
            print("Данная директория уже существует")

    def rmdir(self, filename):
        current_path = self.way.path_to_file(filename)
        try:
            os.rmdir(current_path)
        except FileNotFoundError:
            print("Данной директории не существует")
        except NotADirectoryError:
            print("Файл не является директорией")


    def create_file(self, filename):
        current_path = self.way.path_to_file(filename)
        try:
            open(current_path, "a").close()
        except IsADirectoryError:
            print("Файл уже создан и это является директорией")

    def copy(self, filename, path):
        path_old = self.way.path_to_file(filename)
        if ".." in path:
            path_new = self.way.upper_path + self.sep + filename
        else:
            check = self.way.path_to_file(path)

            if os.path.isdir(check):
                path_new = self.way.path_to_file(path + self.sep + filename)
            else:
                path_new = self.way.path_to_file(path)
        try:
            shutil.copyfile(path_old, path_new)

        except IsADirectoryError:
            shutil.copytree(path_old, path_new)
        except FileNotFoundError:
            print("Данный файл не найден")

    def move(self, filename, path):
        path_old = self.way.path_to_file(filename)
        if ".." in path:
            path_new = self.way.upper_path + self.sep + filename
        else:

            check = self.way.path_to_file(path)
            if os.path.isdir(check):
                path_new = self.way.path_to_file(path + self.sep + filename)
            else:
                path_new = self.way.path_to_file(path)
        try:
            shutil.move(path_old, path_new)
        except FileNotFoundError:
            print("Данный файл не найден")

    def write(self, filename, *data):
        text = " ".join(data)
        path = self.way.path_to_file(filename)
        try:
            with open(path, "a") as file:
                file.write(text)
        except IsADirectoryError:
            print("Не возможно записать данные в директорию")

    def cat(self, filename: str):
        current_path = self.way.path_to_file(filename)
        try:
            with open(current_path, "r") as file:
                print(file.read())
        except FileNotFoundError:
            print("Данного файла не существует")
        except IsADirectoryError:
            print("Файл является директорией")

    def rename(self, old_name, new_name):

        path_old = self.way.path_to_file(old_name)
        path_new = self.way.path_to_file(new_name)

        # Проверка на то, чтоб файл с новым именем не существовал
        try:
            if not os.path.isfile(path_new):
                os.rename(path_old, path_new)
            else:
                print("Файл с данным названием уже существует")
        except FileNotFoundError:
            print("Файла не существует")

    def remove(self, filename):
        path = self.way.path_to_file(filename)
        if os.path.isfile(path):
            os.remove(path)
        else:
            print("Файла не существует")



    def get_command(self, command: str):

        commands = [
            self.cd,
            self.ls,
            self.mkdir,
            self.rmdir,
            self.create_file,
            self.remove,
            self.rename,
            self.cat,
            self.copy,
            self.move,
            self.write,
        ]
        item_dict = dict(zip(COMMANDS_DICT.keys(), commands))
        return item_dict.get(command)


class Paths:

    def __init__(self, sep):
        self.sep = sep
        self.way = [MAIN_PATH]

    @property
    def path(self):
        locale_way = pathlib.Path(__file__).parent.absolute()
        return str(locale_way) + self.sep + self.sep.join(self.way)

    @property
    def upper_path(self):
        locale_way = pathlib.Path(__file__).parent.absolute()
        return str(locale_way) + self.sep + self.sep.join(self.way[:1])

    def add_path(self, path):

        if ".." in path and len(self.way) != 1:
            self.way.pop(-1)
        elif ".." in path:
            print("Выход за пределы директории! У вас нет доступа")
        else:
            self.way.append(path)

    def path_to_file(self, file_name):
        locale_way = self.way.copy()
        locale_way.append(file_name)
        system_path = pathlib.Path(__file__).parent.absolute()
        return str(system_path) + self.sep + self.sep.join(locale_way)


def FilesManager():
    handler = CommandHandler()
    print(f"\n{HELP}")

    while True:
        command = input("\nВведите команду ⋅-> ").split()
        if command[0] == "exit":
            break

        result = handler.get_command(command[0])
        if result:
            try:
                result(*command[1:])
            except TypeError:
                print("Команда вызвана с некорректными аргументами")

        else:
            print(f"Команда не найдена! \n{HELP}")

    print("Выход из файлового менеджера...")


if __name__ == "__main__":
    FilesManager()
