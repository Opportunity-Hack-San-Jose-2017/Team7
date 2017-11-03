from platobot.workers.manager import Manager


if __name__ == "__main__":
    manager = Manager(1, 'Chatty')
    manager.start()
