import json
import logging
import socket
import threading

DEFAULT_PORT = 10100
DEFAULT_IP = "127.1.0.1"
msg_end = "CRLF"


logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    handlers=[logging.FileHandler("./logs/client.log")],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = None

        sock = socket.socket()
        sock.setblocking(1)
        sock.connect((self.ip, self.port))
        self.sock = sock
        logging.info(f"Успешное соединение с сервером {self.ip}:{self.port}")

        self.authorization()

        t = threading.Thread(target=self.read_message)
        t.daemon = True
        t.start()

        self.user_processing()

    def registartion(self, password):
        print("|Регистрация|")
        while True:
            in_username = input("Введите имя пользователя: ")
            if in_username == "":
                print("Пустое имя запрещено!")
            else:
                data = json.dumps(
                    {"password": password, "username": in_username},
                    ensure_ascii=False,
                )
                self.sock.send(data.encode())
                logger.info(f"Отправка данных серверу: '{data}'")

                # Получаем данные с сервера
                response = json.loads(self.sock.recv(1024).decode())
                if not response["result"]:
                    raise ValueError(
                        f"Не удалось осуществить регистрацию"
                    )
                logger.info("Успешно зарегистрировались")
                break

    def authorization(self):
        """Логика авторизации клиента"""
        login_iter = 1
        while True:

            user_password = input("Введите пароль авторизации\n" \
                                  "Если это ваш первый вход в систему, то он будет использоваться для последующей " \
                                  "авторизации в системе -> ")
            if user_password != "":

                data = json.dumps({"password": user_password}, ensure_ascii=False)
                self.sock.send(data.encode())
                logger.info(f"Отправка данных серверу: '{data}'")
                answer = json.loads(self.sock.recv(1024).decode())

                if answer["result"]:
                    print("Авторизация прошла успешно:")
                    break
                elif answer["description"] == "wrong pass":
                    print("Неверный пароль!")
                    sock = socket.socket()
                    sock.setblocking(1)
                    sock.connect((self.ip, self.port))
                    self.sock = sock
                    logging.info(f"Успешное соединение с сервером {self.ip}:{self.port}")

                elif answer["description"] == "registration":
                    sock = socket.socket()
                    sock.setblocking(1)
                    sock.connect((self.ip, self.port))
                    self.sock = sock
                    logging.info(f"Успешное соединение с сервером {self.ip}:{self.port}")
                    self.registartion(user_password)
                    sock = socket.socket()
                    sock.setblocking(1)
                    sock.connect((self.ip, self.port))
                    self.sock = sock
                    logging.info(f"Успешное соединение с сервером {self.ip}:{self.port}")

                else:
                    raise ValueError(
                        f"Ошибка в работе сервера"
                    )

            else:
                print("Пароль не может быть пустым")

            login_iter += 1

    def read_message(self):
        data = ""
        while True:
            buff = self.sock.recv(1024)
            data += buff.decode()

            if msg_end in data:
                logger.info(f"Прием данных от сервера: '{data}'")
                data = data.replace(msg_end, "")

                data = json.loads(data)
                message_text, user_name = data["text"], data["username"]

                print(f"[{user_name}] {message_text}")
                data = ""
            else:
                logger.info(f"Приняли часть данных от сервера: '{data}'")

    def send_message(self, message):
        message += msg_end

        self.sock.send(message.encode())
        logger.info(f"Отправка данных серверу: '{message}'")

    def user_processing(self):

        while True:
            msg = input()
            if msg == "exit":
                break

            self.send_message(msg)

    def __del__(self):
        if self.sock:
            self.sock.close()
        logger.info("Разрыв соединения с сервером")


def port_test(port, check_open=False):
    try:
        port = int(port)
        if 1 <= port <= 65535:
            if check_open:
                try:
                    sock = socket.socket()
                    sock.bind(("", port))
                    sock.close()
                    print(f"Порт свободен - {port}")
                    return True
                except OSError:
                    print(f"Порт занят - {port}")
                    return False

            return True
        print(f"Порт некоректен")
        return False
    except ValueError:
        print(f"Введённое значение не является числом!")
        return False


def ip_test(address):

    error = f"Некорректный ip-адрес"
    success = f"Корректный ip-адрес"
    try:
        socket.inet_pton(socket.AF_INET, address)
    except:
        print(error)
        return False

    print(success)
    return True


def main():
    port_input = input("Введите номер порта сервера -> ")
    port_flag = port_test(port_input)

    if not port_flag:
        port_input = DEFAULT_PORT
        print(f"Выставили порт {port_input} по умолчанию")

    ip_input = input("Введите ip-адрес сервера -> ")
    ip_flag = ip_test(ip_input)

    if not ip_flag:
        ip_input = DEFAULT_IP
        print(f"Выставили ip-адрес {ip_input} по умолчанию")

    Client(ip_input, int(port_input))


if __name__ == "__main__":
    main()
