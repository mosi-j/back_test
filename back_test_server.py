from time import sleep
from datetime import datetime
from new_database import Database
from app import App
import ast
from my_time import time_to_second
from termcolor import colored
import threading

from copy import deepcopy
import os
from server_setting import status_folder_name, status_file_profix

server_status_running = 'running'
server_status_stopping = 'stopping'
server_status_stop = 'stop'

server_status_shutting_down = 'shutting down'
server_status_shutdown = 'shutdown'

server_status_sleeping = 'sleeping'
server_status_waiting = 'waiting'


class BackTestSingleOrderObj(threading.Thread):
    def __init__(self, data, running_list, db_web_order, order_id):
        self.print_color = 'red'
        self.data = data
        self.running_list = running_list
        self.db_web_order = db_web_order
        self.order_id = order_id

        self.adjusted_type = data['adjusted_type']
        self.start_date_time = data['start_date_time']
        self.end_date_time = data['end_date_time']
        self.time_frame = data['time_frame']
        self.max_benefit_up = data['max_benefit_up']
        self.max_benefit_down = data['max_benefit_down']
        self.order_total = data['order_total']
        self.order_same = data['order_same']
        self.data_type = data['data_type']
        self.output_format = data['output_format']
        self.strategy = data['strategy']
        self.en_symbol_12_digit_code = data['en_symbol_12_digit_code']

        self.start_running_time = datetime.now()

        # threading.Thread.__init__(self, name=str(self.last_thread_id))
        threading.Thread.__init__(self)

    def print_c(self, text, color=None):
        try:
            if color is None:
                print(colored(text, self.print_color))
            else:
                print(colored('| ', self.print_color) + colored(text, color))
        except Exception as e:
            # self.__print_c(str(e), 'red')
            print(str(e))

    def process(self):
        app = App(self.strategy, self.output_format, self.start_date_time, self.end_date_time, self.time_frame,
                  self.adjusted_type, self.max_benefit_up, self.max_benefit_down,
                  self.order_total, self.order_same, self.data_type)

        app.set_en_symbol_12_digit_code_list([self.en_symbol_12_digit_code])
        result = app.run()

        run_time = (datetime.now() - self.start_running_time).total_seconds()
        start_time = time_to_second(self.start_running_time)

        self.db_web_order.insert_web_order_sub_result(order_id=self.order_id, symbol=self.en_symbol_12_digit_code,
                                                      result=str(result), start_run_time=str(start_time),
                                                      run_time=run_time)

        self.running_list.remove(self.en_symbol_12_digit_code)
        # self.print_c('finished thread {0}'.format(0))
        return result

    def run(self):
        self.print_c('start thread {0}'.format(threading.current_thread().getName()))
        result = self.process()
        self.print_c('finished thread {0}'.format(threading.current_thread().getName()))

        return result


class BackTestMultiOrderServer:
    def __init__(self, web_order_db_info, process_name, max_thread=1):
        self.print_color = 'green'

        self.max_thread = max_thread
        self.db_web_order = Database(web_order_db_info)
        self.process_name = process_name

        self.status_file_name = '{}/{}.{}'.format(status_folder_name, self.process_name, status_file_profix)
        self.init_status_file()
        self.set_status(server_status_shutdown)

    def init_status_file(self):
        if not os.path.exists(self.status_file_name):
            if os.path.dirname(self.status_file_name) != '':
                if not os.path.exists(os.path.dirname(self.status_file_name)):
                    os.makedirs(os.path.dirname(self.status_file_name))
            f = open(self.status_file_name, 'w', encoding='utf_8')
            f.close()

    def remove_status_file(self):
        if os.path.exists(self.status_file_name):
            os.remove(self.status_file_name)

    def set_status(self, text):
        f = open(self.status_file_name, 'w', encoding='utf_8')
        f.write(text)
        f.close()

    def get_status(self):
        f = open(self.status_file_name, 'r', encoding='utf_8')
        res = f.readline()
        f.close()
        return res

    def print_c(self, text, color=None):
        try:
            if color is None:
                print(colored(text, self.print_color))
            else:
                print(colored('| ', self.print_color) + colored(text, color))
        except Exception as e:
            # self.__print_c(str(e), 'red')
            print(str(e))

    def run_order(self, order_id, input_params):
        error = None
        result = True
        start_time = 0
        end_time = 0
        sum_run_time = 0
        break_order = False
        # ---------------------
        self.running_list = list()

        self.data = dict()

        self.data['adjusted_type'] = int(input_params['adjusted_type'])
        self.data['start_date_time'] = int(input_params['start_date_time'])
        self.data['end_date_time'] = int(input_params['end_date_time'])
        self.data['time_frame'] = input_params['time_frame']
        self.data['max_benefit_up'] = float(input_params['max_benefit_up']) / 100
        self.data['max_benefit_down'] = float(input_params['max_benefit_down']) / 100
        self.data['order_total'] = int(input_params['order_total'])
        self.data['order_same'] = int(input_params['order_same'])
        self.data['data_type'] = input_params['data_type']
        self.data['output_format'] = input_params['output_format']
        self.data['strategy'] = input_params['strategy']
        # self.data['strategy'] = (input_params['strategy_variable'], input_params['strategy_context'])

        max_try = 3
        try_num = 0
        while try_num < max_try or break_order is False:
            try_num += 1
            self.waiting_list = deepcopy(input_params['en_symbol_12_digit_code_list'])
            # self.waiting_list = deepcopy(input_params['accepted_symbol_list'])
            self.running_list = list()

            self.print_c('try number: {0}'.format(try_num))
            q = 0
            print(self.waiting_list)
            waiting_list_count = len(self.waiting_list)
            print(len(self.waiting_list))
            i = 0
            while len(self.waiting_list) > 0:
                i += 1
                if i > 20:
                    i = 0
                    if self.db_web_order.exist_order(order_id) is not True:
                        try_num = max_try
                        break_order = True
                        break

                if threading.active_count() - 1 < self.max_thread + q:
                    # get symbol
                    while True:
                        if len(self.waiting_list) == 0:
                            en_symbol_12_digit_code = None
                            break

                        en_symbol_12_digit_code = self.waiting_list.pop()
                        # print(self.waiting_list)
                        print('wait list len: {0} symbol: {1}'.format(len(self.waiting_list), en_symbol_12_digit_code))

                        # check execute symbol in order
                        res = self.db_web_order.exist_sub_order_result(order_id, en_symbol_12_digit_code)
                        if res is True:
                            continue

                        if en_symbol_12_digit_code in self.running_list:
                            continue

                        self.running_list.append(en_symbol_12_digit_code)
                        break

                    if en_symbol_12_digit_code is None:
                        continue

                    self.data['en_symbol_12_digit_code'] = en_symbol_12_digit_code

                    self.print_c('create thread {0}. thread count: {1}'.format(
                        en_symbol_12_digit_code, threading.active_count() - 1))
                    t = BackTestSingleOrderObj(self.data, self.running_list, self.db_web_order, order_id)
                    # sleep(0.1)
                    t.setName(en_symbol_12_digit_code)
                    t.start()
                    while not t.is_alive():
                        sleep(0.1)
                else:
                    self.print_c('wait for free thread. thread count: {0}'.format(threading.active_count() - 1))
                    sleep(0.1)

            if break_order is True:
                break
            # wait to finish run order threads
            self.print_c('empty wait list')
            while threading.active_count() > 1 + q:
                i += 1
                if i > 20:
                    i = 0
                    if self.db_web_order.exist_order(order_id) is not True:
                        break_order = True
                        break
                self.print_c('wait to finish thread. thread count: {0}'.format(threading.active_count()-1))
                sleep(1)
            # sleep(1)

            if break_order is True:
                break

            all_result, err = self.db_web_order.get_all_sub_result(order_id)
            # symbol, result, start_time, run_time
            if err is not None:
                error = err
                result = False
                self.print_c(err)

            else:
                if len(all_result) < waiting_list_count:
                    if try_num == max_try:
                        break

                    if self.db_web_order.exist_order(order_id) is not True:
                        break_order = True
                        break

                # self.print_c(all_result)
                if len(all_result) > 0:
                    start_time = all_result[0][2]
                    end_time = all_result[0][2]
                    # run_time = 0
                    opt = list()
                    for item in all_result:
                        if start_time > item[2]:
                            start_time = item[2]

                        if end_time < item[2] + item[3]:
                            end_time = item[2] + item[3]

                        sum_run_time += item[3]
                        opt_item = ast.literal_eval(item[1])
                        opt.append(opt_item)
                    self.print_c('2')
                    error = None
                    result = opt

                else:
                    error = None
                    result = None

                break
        # cant complete process
        if try_num == max_try:
            error = 'cant complete process'

        if break_order is True:
            error = 'order not exist'

        order_run_time = end_time - start_time
        return result, start_time, order_run_time, sum_run_time, error

    def run(self, clean_sub_order_result=False):
        self.set_status(server_status_running)

        while self.get_status() != server_status_shutting_down:
            # m += 1
            while self.get_status() in [server_status_stopping, server_status_stop]:
                self.set_status(server_status_stop)
                sleep(10)

            if self.get_status() == server_status_shutting_down:
                continue

            # get order
            avg_order_run_time = 60 * 30
            order, err = self.db_web_order.get_order_new(order_run_time=avg_order_run_time)
            if err is not None:
                if self.get_status() in [server_status_stopping, server_status_shutting_down]:
                    continue

                if err == 'no any order':
                    # clear sub result table
                    self.db_web_order.clean_sub_order_table()

                    self.set_status(server_status_waiting)
                    # self.set_status(server_status_stop)
                    self.print_c('{0}: no any order: wait 60 second'.format(self.process_name))
                    sleep(60)

                else:
                    self.set_status(server_status_sleeping)
                    self.print_c('{0}: error: {1} --> wait 10 second'.format(err, self.process_name))
                    sleep(10)
                continue

            username = order[1]
            order_id = order[0]
            input_params = ast.literal_eval(order[2])

            # -----------------------------------------------------
            # run order
            self.set_status(server_status_running)

            result, start_time, order_run_time, sum_run_time, error = self.run_order(order_id, input_params)

            if error is None:
                # insert result to db
                res, err = self.db_web_order.insert_web_order_result(order_id=order_id,
                                                                     username=username,
                                                                     input_param=str(input_params),
                                                                     result=str(result),
                                                                     start_time=start_time,
                                                                     order_run_time=order_run_time,
                                                                     sum_run_time=sum_run_time)
                if err is not None:
                    if self.get_status() in [server_status_stopping, server_status_shutting_down]:
                        self.print_c('{0}: error: {1}'.format(self.process_name, err))
                        continue

                    self.set_status(server_status_sleeping)
                    self.print_c('{0}: error: {1} --> wait 10 second'.format(self.process_name, err))
                    sleep(10)
                    continue

                self.print_c('{}: finish: insert_web_order_result'.format(self.process_name))
                # res, err = self.db_analyze_data.insert_back_test_result(order_id=order_id,
                #                                                        username=username,
                #                                                        input_param=str(input_params),
                #                                                        result=str(result),
                #                                                        start_time=start_time,
                #                                                        order_run_time=order_run_time,
                #                                                        sum_run_time=sum_run_time)
                # self.print_c('finish: insert_back_test_result')

                self.print_c('{0}: finish run order: {1} : result: {2}'.format(self.process_name, order_id, result))

                # remove order from waiting_order table
                self.db_web_order.remove_order(order_id)

                # remove sub order from sub_order_result table
                if clean_sub_order_result is True:
                    self.db_web_order.clean_sub_order_result(order_id)

            else:
                if self.get_status() in [server_status_stopping, server_status_shutting_down]:
                    self.print_c('{0}: fail run order: {1} result: {2} error: {3}'
                                 .format(self.process_name, order_id, result, error))
                    continue

                self.set_status(server_status_sleeping)
                self.print_c('{0}: fail run order: {1} result: {2} error: {3} --> wait 10 second'
                             .format(self.process_name, order_id, result, error))
                sleep(10)

        self.set_status(server_status_shutdown)


if __name__ == '__main__':
    # from my_database_info import get_database_info, vps1_local_access, website_data
    from server_setting import web_order_db_info
    max_thread = 50
    # web_order_db_info = get_database_info(pc_name=vps1_local_access, database_name=website_data)
    server = BackTestMultiOrderServer(web_order_db_info=web_order_db_info,
                                      process_name='test',
                                      max_thread=max_thread)

    server.run()
