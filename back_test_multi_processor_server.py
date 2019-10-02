from back_test_server import BackTestMultiOrderServer
from back_test_server import server_status_stop, server_status_stopping, server_status_waiting, server_status_running
from back_test_server import server_status_shutdown, server_status_shutting_down, server_status_sleeping

from server_setting import status_folder_name, status_file_profix

from my_time import get_now_time_second
from time import sleep
from multiprocessing import Process
from termcolor import colored


class BackTestSingleProcessServerObj(Process):
    def __init__(self, web_order_db_info, process_name, max_thread):
        self.process_name = process_name
        self.back_test_server = BackTestMultiOrderServer(web_order_db_info=web_order_db_info,
                                                         main_process_name=process_name,
                                                         max_thread=max_thread)

        self.status_file_name = '{0}/{1}.{2}'.format(status_folder_name, self.process_name, status_file_profix)

        Process.__init__(self, name=str(self.process_name))

    def set_status(self, text):
        f = open(self.status_file_name, 'w', encoding='utf_8')
        f.write(text)
        f.close()

    def get_status(self):
        f = open(self.status_file_name, 'r', encoding='utf_8')
        res = f.readline()
        f.close()
        return res

    def status(self):
        return self.get_status()

    def server_shutdown(self):
        self.set_status(server_status_shutting_down)

    def server_start(self):
        self.set_status(server_status_running)

    def server_stop(self):
        self.set_status(server_status_stopping)

    def process(self):
        self.back_test_server.run(clean_sub_order_result=False)

    def run(self, clean_sub_order_result=False):
        print('-- process start -- {}'.format(self.process_name))
        self.process()
        print('-- process stop -- {}'.format(self.process_name))

        # self.bt.shutdown()


class BackTestMultiProcessServer:
    def __init__(self, web_order_db_info, max_process_count, process_max_thread, cycle_time, process_name=''):
        self.process_list = list()
        self.web_order_db_info = web_order_db_info
        self.cycle_time = cycle_time
        self.max_process_count = max_process_count
        self.process_name = process_name + '_'
        self.process_max_thread = process_max_thread
        self.process_sub_name = 0
        self.print_color = 'red'

    def print_c(self, text, color=None):
        try:
            if color is None:
                print(colored(text, self.print_color))
            else:
                print(colored('| ', self.print_color) + colored(text, color))
        except Exception as e:
            # self.__print_c(str(e), 'red')
            print(str(e))

    def run(self):
        while True:
            start = get_now_time_second()

            self.print_c('server count: {}'.format(len(self.process_list)))
            for p in self.process_list:
                self.print_c('{0}: {1}'.format(p.name, p.status()), 'yellow')

            wait_process_count = 0
            sleeping_process_count = 0
            stop_process_count = 0
            stopping_process_count = 0
            shutting_down_process_count = 0
            shutdown_process_count = 0

            # print(self.process_list)
            for process in self.process_list:
                p = process.status()
                # self.print_c(p)
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

            if len(self.process_list) > self.max_process_count:
                # self.print_c('if len(process_list) > max_process_count: {}'.format(len(self.process_list)))
                if shutdown_process_count > 0:
                    for p in self.process_list:
                        if p.status() in [server_status_shutdown]:
                            self.process_list.remove(p)
                            break

                elif shutting_down_process_count > 0:
                    sleep(1)

                elif stop_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_stop:
                            p.server_shutdown()
                            sleep(1)
                            break

                elif sleeping_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_sleeping:
                            p.server_shutdown()
                            sleep(1)
                            break

                elif wait_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_waiting:
                            p.server_shutdown()
                            sleep(1)
                            break

                elif stopping_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_stopping:
                            p.server_shutdown()
                            sleep(1)
                            break

                else:
                    self.process_list[0].server_shutdown()
                    sleep(1)

            elif wait_process_count > (1 + self.max_process_count * 0.2):
                # self.print_c('elif wait_process_count > (1 + max_process_count * 0.2):
                # {}'.format(len(self.process_list)))
                for p in self.process_list:
                    if p.status() == server_status_waiting:
                        self.print_c('{0}: change status: {1} --> {2}'.format(p.name, p.status(), 'stopping'),
                                     'green')
                        p.server_stop()
                        break

            elif wait_process_count == 0:
                # self.print_c('elif wait_process_count == 0: {}'.format(len(self.process_list)))

                # print('++++++++++')
                # print('wait_process_count : {}'.format(wait_process_count))
                # print('sleeping_process_count : {}'.format(sleeping_process_count))
                # print('stop_process_count : {}'.format(stop_process_count))
                # print('stopping_process_count : {}'.format(stopping_process_count))
                # print('shutting_down_process_count : {}'.format(shutting_down_process_count))
                # print('shutdown_process_count : {}'.format(shutdown_process_count))
                # print('++++++++++')
                if stopping_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_stopping:
                            self.print_c('{0}: change status: {1} --> {2}'.format(p.name, p.status(), 'running'),
                                         'green')
                            p.server_start()
                            break

                elif stop_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_stop:
                            self.print_c('{0}: change status: {1} --> {2}'.format(p.name, p.status(), 'running'),
                                         'green')
                            p.server_start()
                            break

                elif shutting_down_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_shutting_down:
                            self.print_c('{0}: change status: {1} --> {2}'.format(p.name, p.status(), 'running'),
                                         'green')
                            p.server_start()
                            break

                elif shutdown_process_count > 0:
                    for p in self.process_list:
                        if p.status() == server_status_shutdown:
                            self.print_c('{0}: change status: {1} --> {2}'.format(p.name, p.status(), 'running'),
                                         'green')
                            p.server_start()
                            break

                elif len(self.process_list) < self.max_process_count:
                    self.process_sub_name += 1
                    process_name = self.process_name + str(self.process_sub_name)
                    self.print_c('create new process: {0}'.format(process_name), 'green')
                    self.process_list.append(BackTestSingleProcessServerObj(process_name=process_name,
                                                                            max_thread=self.process_max_thread,
                                                                            web_order_db_info=self.web_order_db_info))

                    self.process_list[-1].start()

            self.print_c('-------------')
            cycle_run_tim = get_now_time_second() - start
            if cycle_run_tim < self.cycle_time:
                t = self.cycle_time - start + get_now_time_second()
                self.print_c('sleep in: {}'.format(t), 'blue')

                sleep(t)
                self.print_c('sleep out', 'blue')


if __name__ == '__main__':
    from server_setting import back_test_multi_process_server_process_name, \
        back_test_multi_process_server_cycle_time, back_test_multi_process_server_process_max_thread, \
        back_test_multi_process_server_max_process_count, web_order_db_info

    s = BackTestMultiProcessServer(web_order_db_info=web_order_db_info,
                                   max_process_count=back_test_multi_process_server_max_process_count,
                                   process_max_thread=back_test_multi_process_server_process_max_thread,
                                   cycle_time=back_test_multi_process_server_cycle_time,
                                   process_name=back_test_multi_process_server_process_name
                                   )
    s.run()
