from back_test_server import BackTestServer
from my_time import get_now_time_second
from time import sleep

from back_test_server import server_status_stop, server_status_stopping, server_status_waiting, \
    server_status_shutdown, server_status_shutting_down, server_status_sleeping
from server_setting import web_order_db_info

from multiprocessing import Process
from termcolor import colored


class BackTestMultiProcess(Process):
    def __init__(self, process_name, status):
        self.process_name = process_name
        self._status = status
        self.bt = BackTestServer(web_order_db_info=web_order_db_info, status=self._status, main_process_name=self.process_name, max_thread=10)

        Process.__init__(self, name=str(self.process_name))
        # Process.__init__(self)

    def status(self):
        return self._status[self.process_name]
        #return self.bt.status()

    def server_shutdown(self):
        self.bt.shutdown()

    def server_start(self):
        self.bt.start()

    def server_stop(self):
        self.bt.stop()

    def process(self):
        self.bt.run_new()

    def run(self):
        print('-- process start -- 1')
        self.process()
        print('-- process stop -- 2')

        # self.bt.shutdown()

print_color = 'red'
def print_c(text, color=None):
    try:
        if color is None:
            print(colored(text, print_color))
        else:
            print(colored('| ', print_color) + colored(text, color))
    except Exception as e:
        # self.__print_c(str(e), 'red')
        print(str(e))

def run():
    process_list = list()
    cycle_time = 60 * 0.1
    max_process_count = 2
    process_name = 0
    status = dict()
    while True:
        print_c('process_list len: {}'.format(len(process_list)))

        start = get_now_time_second()

        wait_process_count = 0
        sleeping_process_count = 0
        stop_process_count = 0
        stopping_process_count = 0
        shutting_down_process_count = 0
        shutdown_process_count = 0

        print(process_list)
        for process in process_list:
            p = process.status()
            if p == server_status_sleeping:
                sleeping_process_count += 1

            if p == server_status_stop:
                stop_process_count += 1

            if p == server_status_stopping:
                stopping_process_count += 1

            if p == server_status_waiting:
                wait_process_count += 1

            if p == server_status_shutting_down:
                shutting_down_process_count += 1

            if p == server_status_shutdown:
                shutdown_process_count += 1

        # print(0)
        if len(process_list) > max_process_count:
            print_c('if len(process_list) > max_process_count: {}'.format(len(process_list)))

            if shutdown_process_count > 0:
                for p in process_list:
                    if p.status() in [server_status_shutdown]:
                        process_list.remove(p)
                        break

            elif shutting_down_process_count > 0:
                sleep(1)

            elif stop_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_stop:
                        p.server_shutdown()
                        sleep(1)
                        break

            elif sleeping_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_sleeping:
                        p.server_shutdown()
                        sleep(1)
                        break

            elif wait_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_waiting:
                        p.server_shutdown()
                        sleep(1)
                        break

            elif stopping_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_stopping:
                        p.server_shutdown()
                        sleep(1)
                        break

            else:
                process_list[0].server_shutdown()
                sleep(1)

        elif wait_process_count > (1 + max_process_count * 0.2):
            print_c('elif wait_process_count > (1 + max_process_count * 0.2): {}'.format(len(process_list)))

            for p in process_list:
                if p.status() == server_status_waiting:
                    p.server_stop()
                    break

        elif wait_process_count == 0:
            print_c('elif wait_process_count == 0: {}'.format(len(process_list)))
            # print('++++++++++')

            for p in process_list:
                print_c(p.status(), 'yellow')

            print('wait_process_count : {}'.format(wait_process_count))
            print('sleeping_process_count : {}'.format(sleeping_process_count))
            print('stop_process_count : {}'.format(stop_process_count))
            print('stopping_process_count : {}'.format(stopping_process_count))
            print('shutting_down_process_count : {}'.format(shutting_down_process_count))
            print('shutdown_process_count : {}'.format(shutdown_process_count))
            # print('++++++++++')
            if stopping_process_count > 0:
                print_c(1, 'green')
                for p in process_list:
                    if p.status() == server_status_stopping:
                        p.server_start()
                        break

            elif stop_process_count > 0:
                print_c(2, 'green')

                for p in process_list:
                    if p.status() == server_status_stop:
                        p.server_start()
                        break

            elif shutting_down_process_count > 0:
                print_c(3, 'green')

                for p in process_list:
                    if p.status() == server_status_shutting_down:
                        p.server_start()
                        break

            elif shutdown_process_count > 0:
                print_c(4, 'green')

                for p in process_list:
                    if p.status() == server_status_shutdown:
                        print_c(5, 'green')

                        p.server_start()
                        break

            elif len(process_list) < max_process_count:
                print('create new process ')
                process_name += 1
                # process_list.append(BackTestServer(web_order_db_info=web_order_db_info, max_thread=10))
                process_list.append(BackTestMultiProcess(str(process_name), status))
                process_list[-1].start()

        print(start)
        # sleep(10)
        # for p in process_list:
        #    print(p.status())
        print_c('-------------')
        cycle_run_tim = get_now_time_second() - start
        if cycle_run_tim < cycle_time:
            t = cycle_time - start + get_now_time_second()
            print_c('sleep in: {}'.format(t), 'blue')

            sleep(t)
            print_c('sleep out', 'blue')

def run0():
    process_list = list()
    cycle_time = 60 * 0.1
    max_process_count = 1
    process_id = 0
    status = []
    while True:
        print('process_list len: {}'.format(len(process_list)))

        start = get_now_time_second()

        wait_process_count = 0
        sleeping_process_count = 0
        stop_process_count = 0
        stopping_process_count = 0
        shutting_down_process_count = 0
        shutdown_process_count = 0

        print(process_list)
        for process in process_list:
            p = process.status()
            if p == server_status_sleeping:
                sleeping_process_count += 1

            if p == server_status_stop:
                stop_process_count += 1

            if p == server_status_stopping:
                stopping_process_count += 1

            if p == server_status_waiting:
                wait_process_count += 1

            if p == server_status_shutting_down:
                shutting_down_process_count += 1

            if p == server_status_shutdown:
                shutdown_process_count += 1

        # print(0)
        if len(process_list) > max_process_count:
            print('if len(process_list) > max_process_count: {}'.format(len(process_list)))

            if shutdown_process_count > 0:
                for p in process_list:
                    if p.status() in [server_status_shutdown]:
                        process_list.remove(p)
                        break

            elif shutting_down_process_count > 0:
                sleep(1)

            elif stop_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_stop:
                        p.server_shutdown()
                        sleep(1)
                        break

            elif sleeping_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_sleeping:
                        p.server_shutdown()
                        sleep(1)
                        break

            elif wait_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_waiting:
                        p.server_shutdown()
                        sleep(1)
                        break

            elif stopping_process_count > 0:
                for p in process_list:
                    if p.status() == server_status_stopping:
                        p.server_shutdown()
                        sleep(1)
                        break

            else:
                process_list[0].server_shutdown()
                sleep(1)

        elif wait_process_count > (1 + max_process_count * 0.2):
            print('elif wait_process_count > (1 + max_process_count * 0.2): {}'.format(len(process_list)))

            for p in process_list:
                if p.status() == server_status_waiting:
                    p.server_stop()
                    break

        elif wait_process_count == 0:
            print('elif wait_process_count == 0: {}'.format(len(process_list)))
            print('++++++++++')

            for p in process_list:
                print(p.status())

            print('wait_process_count : {}'.format(wait_process_count))
            print('sleeping_process_count : {}'.format(sleeping_process_count))
            print('stop_process_count : {}'.format(stop_process_count))
            print('stopping_process_count : {}'.format(stopping_process_count))
            print('shutting_down_process_count : {}'.format(shutting_down_process_count))
            print('shutdown_process_count : {}'.format(shutdown_process_count))
            print('++++++++++')
            if stopping_process_count > 0:
                print(1)
                for p in process_list:
                    if p.status() == server_status_stopping:
                        p.server_start()
                        break

            elif stop_process_count > 0:
                print(2)

                for p in process_list:
                    if p.status() == server_status_stop:
                        p.server_start()
                        break

            elif shutting_down_process_count > 0:
                print(3)

                for p in process_list:
                    if p.status() == server_status_shutting_down:
                        p.server_start()
                        break

            elif shutdown_process_count > 0:
                print(4)

                for p in process_list:
                    if p.status() == server_status_shutdown:
                        print(5)

                        p.server_start()
                        break

            elif len(process_list) < max_process_count:
                print('create new process ')
                process_id += 1
                # process_list.append(BackTestServer(web_order_db_info=web_order_db_info, max_thread=10))
                process_list.append(BackTestMultiProcess(process_id, status))
                process_list[-1].start()

        print(start)
        for p in process_list:
            print(p.status())
        print('-------------')
        cycle_run_tim = get_now_time_second() - start
        if cycle_run_tim < cycle_time:
            print('sleep in')

            sleep(cycle_time - start + get_now_time_second())
            print('sleep out')



if __name__ == '__main__':
    run()
