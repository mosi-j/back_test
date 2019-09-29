from termcolor import colored
#import constant
#import constant_database_data
# from constant_database_data import constant_database_data
#from timeseries import TimeSeriesData
from indicators_obj import *
from output_obj import *
from datetime import datetime

from timeseries import TimeSeriesData
from bt_setting import *
import operator

class BackTest_Data():
    def __init__(self, database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                 time_frame, adjusted_mod, adjusted_type, default_data_type=constant.ts_data_type_close, data_count=10):

        self.time_series_data = TimeSeriesData(database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                                      time_frame, adjusted_mod, adjusted_type, data_count)
        self.base_index = 0

        self.__origin_candle_count = self.time_series_data.origin_data_count
        self.__default_data_type = default_data_type
        # self.en_symbol_12_digit_code = en_symbol_12_digit_code
        # self.start_date_time = start_date_time
        # self.end_date_time = end_date_time
        # self.time_frame = time_frame
        # self.adjusted_mod = adjusted_mod
        # self.adjusted_type = adjusted_type

    def set_base_index(self, base_index):
        self.base_index = base_index
    def get_base_index(self):
        return self.base_index

    def get_origin_candle_count(self):
        return self.__origin_candle_count

    def get_order_benefit_data(self):
        return self.time_series_data.get_order_benefit_data()

    def set_default_data_type(self,default_data_type):
        self.__default_data_type = default_data_type

    def get_default_data_type(self):
        return self.__default_data_type

    def get_candle_date(self, candle_index):
        return self.time_series_data.get_candle_date(self.base_index + candle_index)

    def get_data(self, candle_index, candle_count, data_type=None, adjusted_mod = None, adjusted_type = None):
        if data_type is None:
            data_type = self.__default_data_type
        return self.time_series_data.get_data(candle_index + self.base_index, candle_count, data_type, adjusted_mod = adjusted_mod, adjusted_type = adjusted_type)


class signal():
    def __init__(self, bt_data):
        self.bt_data:BackTest_Data = bt_data
        self.signal_list = list()

    def reset(self):
        self.signal_list = []

    def sell(self):
        date = self.bt_data.get_candle_date(0)[0]
        price = self.bt_data.get_data(0, 1)[0][0]
        self.signal_list.append({'date':date, 'price':price, 'action':'sell'})

    def buy(self):
        date = self.bt_data.get_candle_date(0)[0]
        price = self.bt_data.get_data(0, 1)[0][0]
        self.signal_list.append({'date': date, 'price': price, 'action': 'buy'})

    def hold(self):
        date = self.bt_data.get_candle_date(0)[0]
        price = self.bt_data.get_data(0, 1)[0][0]
        self.signal_list.append({'date': date, 'price': price, 'action': 'hold'})

    def get_signal(self, sort_type='asc'):
        if sort_type == 'asc':
            self.signal_list.sort(key=operator.itemgetter('date'))
        elif sort_type == 'desc':
            self.signal_list.sort(key=operator.itemgetter('date'), reverse=True)

        return self.signal_list


class orders():
    def __init__(self, signal_obj, total, same):
        self.signal:signal = signal_obj
        self.order_list = list()
        self.default_calc_type = [total, same]


    def set_default_calc_type(self, total, same):
        if total is not None and same is not None:
            if same > total:
                error = 'invalid calc data'
                return error
        else:
            self.default_calc_type = [total, same]
            return None

    def get_orders(self, calc_type=None):
        if calc_type is None:
            calc = self.default_calc_type
        else:
            calc = calc_type

        signal = self.signal.get_signal()

        position_list = list()
        adjusted_list = self.signal.bt_data.time_series_data.get_order_benefit_data()

        last_signal = None
        res = list()
        for i in range(len(signal) - calc[0]):
            sell = 0
            buy = 0
            for j in range(calc[0]):
                if signal[i + j]['action'] == 'sell':
                    sell += 1
                    if sell >= calc[1]:
                        if last_signal != 'sell':
                            last_signal = 'sell'
                            res.append({'date': signal[i + j]['date'], 'price': signal[i + j]['price'],
                                        'action': 'sell'})
                    if buy != 0:
                        buy = 0

                if signal[i + j]['action'] == 'buy':
                    buy += 1
                    if buy >= calc[1]:
                        if last_signal != 'buy':
                            last_signal = 'buy'
                            res.append({'date': signal[i + j]['date'], 'price': signal[i + j]['price'],
                                        'action': 'buy'})

                    if sell != 0:
                        sell = 0

        a = None
        a_time = None
        b = None
        b_time = None

        for item in res:
            if item['action'] == 'buy':
                a = item['price']
                a_time = item['date']
                b = None
                b_time = None
            elif item['action'] == 'sell':
                if a is not None:
                    b = item['price']
                    b_time = item['date']

                    #adjusted_coeff, err = self.signal.bt_data.time_series_data.get_adjusted_coefficient(int(b_time / 1000000) + 1)
                    # print(b_time)
                    # print(adjusted_coeff)

                    #coeff = 1
                    #for item in adjusted_coeff:
                    #    if item[0] > int(a_time / 1000000):
                    #        coeff *= item[1]
                    #    else:
                    #        break

                    res = b
                    for adj in adjusted_list:
                        if adj[0] * 1000000 < a_time:
                            break

                        if adj[0] * 1000000 <= b_time:
                            res = res / adj[1] + adj[2]

                    position_list.append((a, b, a_time, b_time, res))

        # return res, position_list
        return position_list

    def get_orders_benefit(self, calc_type=None):
        orders = self.get_orders(calc_type)
        orders_benefit = 1

        buy_percent = 1 + 0.00464
        sell_percent = 1 - 0.00975

        for order in orders:
            orders_benefit *= order[4] * sell_percent / float(order[0]) / buy_percent

        return orders_benefit

    def calc_order_benefit(self, order):
        adjusted_list = self.signal.bt_data.time_series_data.get_order_benefit_data()
        res = order[1]
        for adj in adjusted_list:
            if adj[0] < order[2]:
                break

            if adj[0] < order[3]:
                res = res / adj[1] + adj[2]

        return res


class BackTest():
    def __init__(self, strategy, en_symbol_12_digit_code, start_date_time, end_date_time, time_frame,
                 adjusted_type, max_benefit_up, max_benefit_down, order_total, order_same, default_data_type=constant.ts_data_type_close):

        adjusted_mod = constant.adjusted_mod_now_time

        self.strategy = strategy
        self.bt_data = BackTest_Data(bt_database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                 time_frame, adjusted_mod, adjusted_type, default_data_type, 0)

        self.signal = signal(self.bt_data)

        self.max_benefit_up = max_benefit_up
        self.max_benefit_down = max_benefit_down

        self.max_benefit_order_list = None
        self.max_benefit_profit = None

        self.order_total = order_total
        self.order_same = order_same
        self.orders = orders(self.signal, self.order_total, self.order_same)

        self.run_strategy_error = None

        self.print_color = 'green'

    def print_c(self, text, color=None):
        try:
            if color is None:
                print(colored(text, self.print_color))
            else:
                print(colored('| ', self.print_color) + colored(text, color))
        except Exception as e:
            # self.__print_c(str(e), 'red')
            print(str(e))

    def __calc_max_benefit(self):
        base_index = self.bt_data.get_base_index()
        self.bt_data.set_base_index(0)
        series_data, err = self.bt_data.get_data(0, self.bt_data.get_origin_candle_count(), adjusted_type=constant.adjusted_type_none)
        series_time, err = self.bt_data.get_data(0, self.bt_data.get_origin_candle_count(), data_type=constant.ts_data_type_time)
        series_data.reverse()
        series_time.reverse()
        self.bt_data.set_base_index(base_index)
        # print(series_data)
        # print(series_time)

        up = 1 + self.max_benefit_up
        down = 1 - self.max_benefit_down
        position_list = list()

        if len(series_data) >= 2:
            a = series_data[0]
            b = series_data[0]
            a_time = series_time[0]
            b_time = series_time[0]
            b_visual = self.__calc_sell_price(a, b, a_time, b_time)

            for i in range(len(series_data)):
                ti = series_data[i]
                ti_time = series_time[i]
                ti_virtual = self.__calc_sell_price(a, ti, a_time, ti_time)

                if a < b_visual:  # صعودی
                    if ti_virtual >= b_visual:
                        b = ti
                        b_time = ti_time
                        b_visual = ti_virtual

                    elif ti_virtual > a:
                        if b_visual < a * up:  # حد سود فعال نیست
                            continue
                        else:  # حد سود فعال است
                            if self.__calc_sell_price(b, ti, b_time, ti_time) > b * down:
                                pass
                            else:
                                position_list.append((a, b, a_time, b_time, b_visual))
                                a = b
                                a_time = b_time

                                b = ti
                                b_time = ti_time
                                b_visual = self.__calc_sell_price(a, ti, a_time, ti_time)

                    else:  # ti_virtual <= a
                        if b_visual < a * up:  # حد سود فعال نیست
                            a = b
                            a_time = b_time

                            b = ti
                            b_time = ti_time
                            b_visual = self.__calc_sell_price(a, ti, a_time, ti_time)

                        else:  # حد سود فعال است
                            position_list.append((a, b, a_time, b_time, b_visual))
                            a = b
                            a_time = b_time

                            b = ti
                            b_time = ti_time
                            b_visual = self.__calc_sell_price(a, ti, a_time, ti_time)

                elif a > b_visual:  # نزولی
                    if ti_virtual <= b_visual:
                        b = ti
                        b_time = ti_time
                        b_visual = ti_virtual

                    elif ti_virtual < a:
                        if self.__calc_sell_price(b, ti, b_time, ti_time) > b * up:
                            a = b
                            a_time = b_time

                            b = ti
                            b_time = ti_time
                            b_visual = self.__calc_sell_price(a, ti, a_time, ti_time)

                    else:  # ti_virtual >= a
                        a = b
                        a_time = b_time

                        b = ti
                        b_time = ti_time
                        b_visual = self.__calc_sell_price(a, ti, a_time, ti_time)

                else:  # a = b
                    a = b
                    a_time = b_time
                    b = ti
                    b_time = ti_time
                    b_visual = self.__calc_sell_price(a, ti, a_time, ti_time)

        orders_benefit = 1
        #for order in position_list:
        #    orders_benefit *= order[4] / order[0]

        buy_percent = 1 + 0.00464
        sell_percent = 1 - 0.00975
        for order in position_list:
            orders_benefit *= (order[4] * sell_percent) / (order[0] * buy_percent)
        # print(position_list)
        # print(len(position_list))
        return position_list, orders_benefit

    def __calc_sell_price(self, buy_price, sell_price, buy_time, sell_time):
        adjusted_list = self.bt_data.get_order_benefit_data()

        res = sell_price
        for adj in adjusted_list:
            if adj[0] * 1000000 < buy_time:
                break

            if adj[0] * 1000000 <= sell_time:
                res = res / adj[1] + adj[2]

        return res

    def set_max_benefit_setting(self, max_benefit_up, max_benefit_down):
        self.max_benefit_up = max_benefit_up
        self.max_benefit_down = max_benefit_down
        self.max_benefit_order_list = None
        self.max_benefit_profit = None

    def get_max_benefit_order_list(self):
        if self.max_benefit_order_list is None:
            self.max_benefit_order_list, self.max_benefit_profit = self.__calc_max_benefit()

        return self.max_benefit_order_list

    def get_max_benefit_profit(self):
        if self.max_benefit_profit is None:
            self.max_benefit_order_list, self.max_benefit_profit = self.__calc_max_benefit()

        return self.max_benefit_profit

    def calc_backtest_benefit_str(self, strategy_variable=None, strategy_context=None):
        if strategy_variable is None:
            strategy_variable = self.strategy[0]
        if strategy_context is None:
            strategy_context = self.strategy[1]

        #print(self.bt_data.time_series_data.all_raw_adjusted_data)

        res = self.run_strategy(strategy_variable, strategy_context)
        return self.orders.get_orders(), self.orders.get_orders_benefit()

    def run_strategy(self, strategy_variable, strategy_context):
        body_1 = '''

base_index = self.bt_data.get_base_index()
self.signal.reset()
self.run_strategy_error = None
'''
        body_2 = '''

for i in range(self.bt_data.get_origin_candle_count()):
    self.bt_data.set_base_index(i)

'''
        body_3 = '''

self.bt_data.set_base_index(base_index)

'''
        nested_str = '    '
        s_v = strategy_variable
        s_c = nested_str + strategy_context.replace('\n', '\n' + nested_str)

        body = body_1 + s_v + body_2 + s_c + body_3
        try:
            exec(body)
        except Exception as e:
            self.run_strategy_error = str(e.args)

        return self.run_strategy_error

    # -------------
    def get_candle_date_index(self, candle_date):
        return self.bt_data.time_series_data.get_candle_date_index(candle_date)

    # -++++++++++++++++++++
    def strategy(self):
        base_index = self.bt_data.get_base_index()
        self.signal.reset()
        self.run_strategy_success = None

        try:
            macd = MACD(26, 12, 9, self.bt_data)

            for i in range(self.bt_data.get_origin_candle_count()):
                self.bt_data.set_base_index(i)

                if macd.macd_line(0) > macd.signal_line(0):
                    self.signal.buy()

                elif macd.macd_line(0) < macd.signal_line(0):
                    self.signal.sell()

                else:
                    self.signal.hold()

            self.bt_data.set_base_index(base_index)
        except Exception as e:
            self.run_strategy_success = str(e)

        return None

    def strategy0(self):
        base_index = self.bt_data.get_base_index()
        self.signal.reset()

        macd = MACD(26, 12, 9, self.bt_data)
        for i in range(self.bt_data.get_origin_candle_count()):
            self.bt_data.set_base_index(i)
            macd_res, err = macd.d(0, get_error=True)

            if err is None:
                if macd_res['macd_line'] > macd_res['signal_line']:
                    self.signal.buy()

                elif macd_res['macd_line'] < macd_res['signal_line']:
                    self.signal.sell()

                else:
                    self.signal.hold()
            else:
                self.signal.hold()

        self.bt_data.set_base_index(base_index)
        return None

    def calc_backtest_benefit(self):
        self.strategy()
        return self.orders.get_orders(), self.orders.get_orders_benefit()

    def calc_backtest_benefit0(self):
        self.strategy0()
        return self.orders.get_orders(), self.orders.get_orders_benefit()

    def run(self):

        # init objects
        data1 = Data(self.bt_data)
        sma1 = SMA(10, self.bt_data)
        ema1 = EMA(10, self.bt_data)
        macd1 = MACD(20, 10, 9, self.bt_data)
        rsi1 = RSI(10, self.bt_data)
        williams1 = WILLIAMS(10, self.bt_data)

        #for i in range(self.bt_data.get_origin_candle_count()):
        for i in range(10):
            self.bt_data.set_base_index(i)
            print('----------')
            print('data:{}'.format(data1.get_data(0)))
            print('sma:{}'.format(sma1.d(0)))
            print('ema:{}'.format(ema1.d(0)))
            print('macd:{}'.format(macd1.d(0)))
            print('macd slow:{}'.format(macd1.slow(0)))
            print('rsi:{}'.format(rsi1.d(0)))
            print('williams:{}'.format(williams1.d(0)))

            # run strategy

    def run0(self):
        coeff = 10
        get_error = False
        # init objects
        #data1 = Data(self.bt_data)
        sma1 = LWMA(100, self.bt_data)
        sma2 = MACD(20, 10, 9, self.bt_data)
        sma_list1 = LWMA_list(100, self.bt_data)
        sma_list2 = MACD_list(20, 10, 9, self.bt_data)

        sma1_list = list()
        sma2_list = list()
        #data1_list = list()
        start_time = datetime.now()

        for i in range(1 + coeff * self.bt_data.get_origin_candle_count()):
            #print(i)
        #for i in range(10):
            self.bt_data.set_base_index(i)
            #data1_list.append(data1.get_data(0))
            sma1_list.append(sma1.d(0, get_error=get_error))
            sma2_list.append(sma2.macd_histogram(0, get_error=get_error))
        print(datetime.now() - start_time)
        #print(data1_list)
        #print(len(data1_list))
        print(sma1_list)
        #print('-----------------')
        self.bt_data.set_base_index(0)

        start_time = datetime.now()
        a = sma_list1.d(0, 1 + coeff * self.bt_data.get_origin_candle_count(), get_error=get_error)
        b = sma_list2.macd_histogram(0, 1 + coeff * self.bt_data.get_origin_candle_count(), get_error=get_error)
        print(a)
        print('-----------------')

        print(sma2_list)
        print(b)
        #print(len(a))


        print(datetime.now() - start_time)


        #print('----------')
            #print('data;{}'.format(data1_list[i]))
            #print('sma:{}'.format(sma1_list[i]))

            #print('data:{}'.format(data1.get_data(0)))
            #print('sma:{}'.format(sma1.d(0)))

            # run strategy

    def calc_max_benefit0(self):
        self.bt_data.set_base_index(0)
        series_price, err = self.bt_data.get_data(0, self.bt_data.get_origin_candle_count(), adjusted_mod=constant.adjusted_mod_off)
        series_time, err = self.bt_data.get_data(0, self.bt_data.get_origin_candle_count(), data_type=constant.ts_data_type_time, adjusted_mod=constant.adjusted_mod_off)
        #series_data.reverse()
        #series_time.reverse()
        raw_benefit_adjusted_data = self.bt_data.time_series_data.get_order_benefit_data()


        end_price = series_price[0]
        end_date = series_time[0]

        adjusted_time_series = list()

        for i in range(self.bt_data.get_origin_candle_count()):
            res = end_price
            for adj in raw_benefit_adjusted_data:
                if adj[0] * 1000000 < series_time[i]:
                    break

                if adj[0] * 1000000 <= end_date:
                    res = res / adj[1] + adj[2]
            adjusted_time_series.append(series_price[i] *  end_price / res)

        print('--------------')
        print(raw_benefit_adjusted_data)
        print(series_time)
        print(series_price)
        print(adjusted_time_series)
        print(len(adjusted_time_series))
        print('--------------')

        adjusted_time_series.reverse()
        series_time.reverse()
        series_price.reverse()
        max_benefit_coeff = 1

        series_data = adjusted_time_series

        up = 1 + self.max_benefit_up
        down = 1 - self.max_benefit_down
        position_list = list()

        if len(series_data) >= 2:
            a = series_data[0]
            b = series_data[0]
            a_time = series_time[0]
            b_time = series_time[0]

            for i in range(len(series_data)):
                ti = series_data[i]
                if a < b:  # صعودی
                    if ti >= b:
                        b = ti
                        b_time = series_time[i]

                    elif ti > a:
                        if b < a * up:  # حد سود فعال نیست
                            continue
                        else:  # حد سود فعال است
                            if ti > b * down:
                                pass
                            else:
                                position_list.append((a, b, a_time, b_time))
                                a = b
                                b = ti
                                a_time = b_time
                                b_time = series_time[i]
                    else:  # ti <= a
                        if b < a * up:  # حد سود فعال نیست
                            a = b
                            b = ti
                            a_time = b_time
                            b_time = series_time[i]
                        else:  # حد سود فعال است
                            position_list.append((a, b, a_time, b_time))
                            a = b
                            b = ti
                            a_time = b_time
                            b_time = series_time[i]
                elif a > b:  # نزولی
                    if ti <= b:
                        b = ti
                        b_time = series_time[i]

                    elif ti < a:
                        if ti > b * up:
                            a = b
                            b = ti
                            a_time = b_time
                            b_time = series_time[i]

                    else:
                        a = b
                        b = ti
                        a_time = b_time
                        b_time = series_time[i]


                else:  # a = b
                    b = ti
                    b_time = series_time[i]

        # print(position_list)
        # print(len(position_list))
        return position_list

    def calc_max_benefit1(self):
        self.bt_data.set_base_index(0)
        series_data, err = self.bt_data.get_data(0, self.bt_data.get_origin_candle_count())
        series_time, err = self.bt_data.get_data(0, self.bt_data.get_origin_candle_count(), data_type=constant.ts_data_type_time)
        series_data.reverse()
        series_time.reverse()

        up = 1 + self.max_benefit_up
        down = 1 - self.max_benefit_down
        position_list = list()

        if len(series_data) >= 2:
            a = series_data[0]
            b = series_data[0]
            a_time = series_time[0]
            b_time = series_time[0]

            for i in range(len(series_data)):
                ti = series_data[i]
                if a < b:  # صعودی
                    if ti >= b:
                        b = ti
                        b_time = series_time[i]

                    elif ti > a:
                        if b < a * up:  # حد سود فعال نیست
                            continue
                        else:  # حد سود فعال است
                            if ti > b * down:
                                pass
                            else:
                                position_list.append((a, b, a_time, b_time))
                                a = b
                                b = ti
                                a_time = b_time
                                b_time = series_time[i]
                    else:  # ti <= a
                        if b < a * up:  # حد سود فعال نیست
                            a = b
                            b = ti
                            a_time = b_time
                            b_time = series_time[i]
                        else:  # حد سود فعال است
                            position_list.append((a, b, a_time, b_time))
                            a = b
                            b = ti
                            a_time = b_time
                            b_time = series_time[i]
                elif a > b:  # نزولی
                    if ti <= b:
                        b = ti
                        b_time = series_time[i]

                    elif ti < a:
                        if ti > b * up:
                            a = b
                            b = ti
                            a_time = b_time
                            b_time = series_time[i]

                    else:
                        a = b
                        b = ti
                        a_time = b_time
                        b_time = series_time[i]


                else:  # a = b
                    b = ti
                    b_time = series_time[i]

        # print(position_list)
        # print(len(position_list))
        return position_list


if __name__ == '__main__':
    import constant_database_data

    database_info = constant_database_data.laptop_analyze_server_role_db_info
    en_symbol_12_digit_code = 'IRO3PMRZ0001'
    tsetmc_id = '53449700212786324'
    start_date_time = 20180101000000
    end_date_time = 20190611000000
    time_frame = 'D1'
    adjusted_mod = constant.adjusted_mod_off
    adjusted_type = constant.adjusted_type_all
    # adjusted_type = constant.adjusted_type_capital_increase
    # adjusted_type = constant.adjusted_type_all
    data_count = 0
