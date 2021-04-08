import json
import logging
import random
import socket
import threading

from data_help import DataHelp

msg_end = "CRLF"
DEFAULT_PORT = 10100

logging.basicConfig(
    format="%(asctime)s20 [%(levelname)s] %(funcName)s: %(message)s",
    handlers=[logging.FileHandler("./logs/server.log"), logging.StreamHandler()],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, port):

        logging.info(f"Запуск сервера..")
        self.port = port
        self.sock = None
        self.database = DataHelp()

        sock = socket.socket()
        sock.bind(("127.1.0.1", self.port))
        sock.listen()
        self.sock = sock

        self.authorizations = []
        self.registrations = []
        self.connections = []

        self.ip_to_user_dict = {}
        logging.info(f"Сервер инициализирован на порте - {port}")

        while True:
            connection, address = self.sock.accept()

            self.connections.append((connection, address))
            logging.info(f"Новое соединение от {address[0]}")

            t = threading.Thread(target=self.client_process, args=(connection, address))
            t.daemon = True
            t.start()

    def send_message(self, connection, data, ip):
        data_text = data
        if type(data) == dict:
            data = json.dumps(data, ensure_ascii=False)
        data = data.encode()
        connection.send(data)
        logging.info(f"Сообщение {data_text} было отправлено клиенту {ip}")

    def message_get(self, connection, ip):
        data = ""
        while True:
            buff = connection.recv(1024)
            data += buff.decode()
            data += msg_end
            if msg_end in data:

                username = self.ip_to_user_dict[ip]
                logging.info(
                    f"Получили сообщение {data} от клиента {ip} ({username})"
                )
                data = {"username": username, "text": data}

                logger.info(
                    f"Текущее кол-во подключений к серверу: {len(self.connections)}"
                )
                for _connection in self.connections:
                    current_conn, current_ip = _connection
                    try:
                        self.send_message(current_conn, data, current_ip)
                    except BrokenPipeError:
                        continue

                data = ""

            else:
                logger.info(f"Приняли часть данных от клиента {ip}: '{data}'")

            if not buff:
                break

    def registration(self, connection, address):

        data = json.loads(connection.recv(1024).decode())
        password, username = data["password"], data["username"]
        ip = address[0]
        self.database.user_reg(ip, password, username)
        logger.info(f"Клиент {ip} -> регистрация прошла успешно")
        data = {"result": True}
        if ip in self.registrations:
            self.registrations.remove(ip)
            logging.info(f"Удалили клиента {ip} из списка регистрации")

        self.send_message(connection, data, ip)
        logger.info(f"Клиент {ip}. Отправили данные о результате регистрации")

    def authorization(self, connection, address):

        password = json.loads(connection.recv(1024).decode())["password"]

        ip = address[0]

        result, username = self.database.authorization(ip, password)

        if result == 1:
            logger.info(f"Клиент {ip} -> авторизация прошла успешно")
            data = {"result": True, "body": {"username": username}}
            if ip not in self.authorizations:
                self.authorizations.append(ip)
                self.ip_to_user_dict[ip] = username
                logging.info(f"Добавили клиента {ip} в список авторизации")
        elif result == 0:
            logger.info(f"Клиент {ip} -> авторизация не удалась")
            data = {"result": False, "description": "wrong pass"}
        else:
            logger.info(
                f"Клиент {ip} -> необходима предварительная регистрация в системе"
            )
            data = {"result": False, "description": "registration"}
            if ip not in self.registrations:
                self.registrations.append(ip)
                logging.info(f"Добавили клиента {ip} в список регистрации")

        self.send_message(connection, data, ip)
        logger.info(f"Клиент {ip}. Отправили данные о результате авторизации")

        if result == 1:
            self.message_get(connection, ip)

    def client_process(self, connection, address):

        try:
            ip = address[0]

            if ip in self.registrations:
                self.registration(connection, address)

            elif ip not in self.authorizations:
                self.authorization(connection, address)

            else:
                self.message_get(connection, ip)
        except:
            logging.info(f"Отключение клиента {ip}")
            self.connections.remove((connection, address))
            if ip in self.authorizations:
                self.authorizations.remove(ip)
                logging.info(f"Удалили клиента {ip} из списка авторизации")
            print(self.connections)

    def __del__(self):
        logging.info(f"Остановка сервера")


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
    port_input = input("Порт для сервера: ")

    port = port_test(port_input, check_open=True)

    if not port:

        if not port_test(DEFAULT_PORT):
            buff = False
            while not buff:
                port = random.randint(2000, 50000)
                print(f"Порт по умолчанию занят! Сгенерировали рандомный порт - {port}")
                buff = port_test(port)

            port_input = port
        else:
            port_input = DEFAULT_PORT
        print(f"Порт {port_input} выбран по умолчанию")

    Server(int(port_input))


if __name__ == "__main__":
    main()
