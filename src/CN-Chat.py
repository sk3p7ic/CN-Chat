import client.MainWindow
import client.LoginWindow


def main():
    username, password = client.LoginWindow.start()
    print(f"{username} -- {password}")


if __name__ == "__main__":
    main()
