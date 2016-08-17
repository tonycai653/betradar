import re
import threading
import betradar
import time


filename = 'README.txt'
lock = threading.RLock()

def parse(line):
    m = re.search(r'(\d+)\s*-\s(\w+)', line)
    if m:
        return m.group(1)
    else:
        return None


def ids_and_names(file):
    with open(file, 'a') as f:
        return [parse(line) for line in f if line.strip()[0].isdigit()]


def update_readme(f, data):
    while True:
        with open(f, 'a') as fw:
            lock.acquire()
            for ele in data:
                l = ele[0] if isinstance(ele[0], str) else str(ele[0]) + '-' + ele[1] if isinstance(ele[1], str) else str(ele[1])
            fw.writelines(l)
            data.clear()
            lock.release()
        time.sleep(20)

if __name__ == '__main__':

    ids = ids_and_names(filename)
    new_ids = set()

    threading.Thread(target=update_readme, args=(filename, new_ids))
    while True:
        lock.RLock()
        new_ids.add([(ev['_typeid'], ev['name']) for ev in betradar.get_soccer_events() if ev['_typeid'] not in ids])
        lock.release()
        time.sleep(2)
