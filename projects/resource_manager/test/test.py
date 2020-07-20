from time import sleep

from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask


class Foo(ThreadTask):
    def run(self):
        for i in range(0, 10):
            print(i)
        sleep(2)


class Foo1(ThreadTask):
    def run(self):
        for i in range(100, 110):
            print(i)
        sleep(2)


def run():
    pool = ThreadPool.instance()
    thread_task_1 = Foo()
    thread_task_2 = Foo1()

    pool.get_thread().put_job(thread_task_1)

    pool.get_thread().put_job(thread_task_2)

    sleep(3)
    print(ThreadPool.instance().thread_count)
    pool.clean()
