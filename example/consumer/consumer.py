from eventify import Eventify

if __name__ == '__main__':
    ev = Eventify(config='config.json')
    ev.publisher().start()
