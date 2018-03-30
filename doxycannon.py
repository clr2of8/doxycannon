import argparse
import docker
from Queue import Queue
from threading import Thread

VERSION = '0.1.0'
IMAGE = 'audibleblink/doxycannon'
THREADS = 20
doxy = docker.from_env()
# doxy.containers.run("bfirsh/reticulate-splines", detach=True)
# doxy.containers.list()

def build_image():
    return doxy.images.build(path='.', tag='audibleblink/doxycannon')

# def start_containers_from_image(image_name):

def multikill(jobs):
    while True:
        container = jobs.get()
        print 'Stopping: {}'.format(container.name)
        container.kill(9)
        jobs.task_done()

def containers_from_image(image_name):
    jobs = Queue(maxsize=0)
    [jobs.put(cont) for cont in doxy.containers.list() 
     if cont.attrs['Config']['Image'] == image_name]
    return jobs

def stop_containers_from_image(image_name):
    container_queue = containers_from_image(image_name)
    for i in range(THREADS):
        worker = Thread(target=multikill, args=(container_queue,))
        worker.setDaemon(True)
        worker.start()
    container_queue.join()
    print '[+] All container stopped!'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--build',
        action='store_true',
        default=False,
        dest='build',
        help='Builds the base docker image')
    parser.add_argument(
        '--up',
        action='store_true',
        default=False,
        dest='up',
        help='Brings up containers. 1 for each VPN file in ./VPN')
    parser.add_argument(
        '--down',
        action='store_true',
        default=False,
        dest='down',
        help='Bring down all the containers')
    parser.add_argument('--version', action='version', version="%(prog)s {}".format(VERSION))
    args = parser.parse_args()

    if args.build:
        print 'building'
    elif args.up:
        print 'start containers'
    elif args.down:
        stop_containers_from_image(IMAGE)

if __name__ == "__main__":
    main()
