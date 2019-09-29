from back_test import BackTest
from constant import constant
from datetime import datetime
from new_database import Database


class App:
    def __init__(self, strategy, output_format, start_date_time, end_date_time, time_frame,
                 adjusted_type, max_benefit_up, max_benefit_down, order_total, order_same,
                 default_data_type=constant.ts_data_type_close):

        self.en_symbol_12_digit_code_list = list()
        self.strategy = strategy
        self.output_format_list = output_format

        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.time_frame = time_frame
        self.adjusted_type = adjusted_type
        self.max_benefit_up = max_benefit_up
        self.max_benefit_down = max_benefit_down
        self.order_total = order_total
        self.order_same = order_same
        self.default_data_type = default_data_type

        self.output_format_name_list = ['max_benefit', 'back_test_benefit', 'test']

    def set_en_symbol_12_digit_code_list(self, en_symbol_12_digit_code_list):
        self.en_symbol_12_digit_code_list = en_symbol_12_digit_code_list

    def add_en_symbol_12_digit_code_list(self, en_symbol_12_digit_code_list):
        for symbol in en_symbol_12_digit_code_list:
            self.en_symbol_12_digit_code_list.append(symbol)

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_output_format_list(self, output_format):
        self.output_format_list = output_format

    def add_output_format_list(self, output_format_list):
        for output in output_format_list:
            self.output_format_list.append(output)


    def run(self, database_obj=None):
        # print('app - run')
        result = list()
        for symbol in self.en_symbol_12_digit_code_list:
            bt = BackTest(self.strategy, symbol, self.start_date_time, self.end_date_time, self.time_frame, self.adjusted_type,
                          self.max_benefit_up, self.max_benefit_down, self.order_total, self.order_same,
                          self.default_data_type)
            res = list()
            for output in self.output_format_list:
                if output == 'max_benefit':
                    res.append(self.max_benefit_output(bt))

                elif output == 'back_test_benefit':
                    res.append(self.back_test_benefit(bt))
                    #res.append(self.back_test_benefit(bt))

                elif output == 'analyze_strategy':
                    res.append(self.analyze_strategy(bt))
                #print(res)

            if database_obj is None:
                result.append((symbol, res))
            else:
                r, e = database_obj.get_symbols_name(symbol)
                if e is None:
                    result.append((r[0][0], res))
                else:
                    result.append((symbol, res))

        return result

    def test_strategy(self):
        print('app - test_strategy')
        symbol = self.en_symbol_12_digit_code_list[0]
        bt = BackTest(self.strategy, symbol, self.start_date_time, self.end_date_time, self.time_frame,
                      self.adjusted_type,
                      self.max_benefit_up, self.max_benefit_down, self.order_total, self.order_same,
                      self.default_data_type)

        res = bt.run_strategy(self.strategy[0], self.strategy[1])

        if res is None:
            return True, None

        return False, res

    def max_benefit_output(self, bt):
        max_benefit_order_list = bt.get_max_benefit_order_list()
        max_benefit_coeff = bt.get_max_benefit_profit()
        # print(max_benefit_order_list, max_benefit_coeff)

        #result = ('max_benefit', str(max_benefit_order_list) + '/n' + str(max_benefit_coeff))
        #result = ('max_benefit', (('max_benefit_order_list', max_benefit_order_list), ('max_benefit_coeff', max_benefit_coeff)))
        result = ['max_benefit', [['max_benefit_order_list', max_benefit_order_list], ['max_benefit_coeff', max_benefit_coeff]]]

        return result
        #return max_benefit_order_list, max_benefit_coeff

    def back_test_benefit(self, bt):
        #res = bt.calc_backtest_benefit()
        res = bt.calc_backtest_benefit_str()
        print(res)
        #result = ('back_test_benefit', str(res[0]) + '/n' + str(res[1]))
        result = ['back_test_benefit', [['back_test_order_list', str(res[0])], ['back_test_order_coeff', str(res[1])]]]

        return result

    def analyze_strategy(self, bt):
        buy_percent = 1 + 0.00464
        sell_percent = 1 - 0.00975

        # get max benefit
        max_benefit_order_list = bt.get_max_benefit_order_list()
        # max_benefit_order_list = [(37252, 43996, 20180102000000, 20180325000000, 43996), (40132, 54499, 20180506000000, 20180807000000, 59199.0), (48800, 69208, 20180902000000, 20180930000000, 69208), (57900, 64500, 20181007000000, 20181017000000, 64500), (48900, 55289, 20181201000000, 20181219000000, 55289), (50605, 43410, 20190128000000, 20190330000000, 86820.0)]
        # print(max_benefit_order_list)

        max_benefit_profit = bt.get_max_benefit_profit()
        # max_benefit_profit = 4.8962922762239005
        # print(max_benefit_profit)

        # get strategy benefit
        res = bt.calc_backtest_benefit_str()
        # res = ([(41600, 40894, 20180117000000, 20180128000000, 40894), (41500, 42900, 20180313000000, 20180409000000, 42900), (41900, 41900, 20180513000000, 20180528000000, 41900), (42950, 51200, 20180618000000, 20180819000000, 55900.0), (60305, 57900, 20180916000000, 20181007000000, 57900), (51000, 52510, 20181215000000, 20190121000000, 52510), (52870, 38474, 20190204000000, 20190416000000, 76948.0)], 1.7200849848497446)

        #print(res)
        back_test_order_list = res[0]
        back_test_profit = res[1]

        #print('max_benefit_order_list {0}'.format(max_benefit_order_list))
        #print('back_test_order_list   {0}'.format(back_test_order_list))

        # ----------------- analyze -----------------
        # max benefit -----------------
        max_day_in_trade = 0
        for item in max_benefit_order_list:
            # print(item)
            s = bt.get_candle_date_index(item[2]) - bt.get_candle_date_index(item[3])
            # print(s)
            max_day_in_trade += s
        # print(day_in_trade)
        max_order_count = len(max_benefit_order_list)
        # print(order_count)

        # strategy -----------------
        profit = back_test_profit
        day_in_trade = 0
        loss_order_count = 0
        win_order_count = 0

        loss_orders_benefit = 1
        win_orders_benefit = 1
        for item in back_test_order_list:
            # print(item)
            s = bt.get_candle_date_index(item[2]) - bt.get_candle_date_index(item[3])
            # print(s)
            day_in_trade += s

            benefit = item[4] * sell_percent / float(item[0]) / buy_percent
            if benefit > 1:
                win_order_count += 1
                win_orders_benefit *= benefit
            elif benefit < 2:
                loss_order_count += 1
                loss_orders_benefit *= benefit

        all_order_count = len(back_test_order_list)
        equal_order_count = all_order_count - win_order_count - loss_order_count

        if all_order_count == 0:
            win_order_count_ratio = 0
            loss_order_count_ratio = 0
            equal_order_count_ratio =0
        else:
            win_order_count_ratio = win_order_count / all_order_count
            loss_order_count_ratio = loss_order_count / all_order_count
            equal_order_count_ratio = equal_order_count / all_order_count

        #print('--------------------------------------------------------------')
        #print('max day_in_trade: {0}'.format(max_day_in_trade))
        #print('max order_count {0}'.format(max_order_count))
        #print('max profit {0}'.format(max_benefit_profit))#

        #print('strategy_day_in_trade {0}'.format(day_in_trade))
        #print('strategy_profit {0}'.format(profit))
        #print('strategy_all_order_count {0}'.format(all_order_count))
        #print('strategy_win_order_count {0}'.format(win_order_count))
        #print('strategy_loss_order_count {0}'.format(loss_order_count))
        #print('strategy_equal_order_count {0}'.format(equal_order_count))

        #print('win_order_count_ratio {0}'.format(win_order_count_ratio))
        #print('loss_order_count_ratio {0}'.format(loss_order_count_ratio))
        #print('equal_order_count_ratio {0}'.format(equal_order_count_ratio))

        #print('win_orders_benefit {0}'.format(win_orders_benefit))
        #print('loss_orders_benefit {0}'.format(loss_orders_benefit))
        #print('--------------------------------------------------------------')

        result = ['analyze_strategy', [['max_day_in_trade', max_day_in_trade],
                                       ['max_order_count', max_order_count],
                                       ['max_benefit_profit', max_benefit_profit],
                                       ['day_in_trade', day_in_trade],
                                       ['profit', profit],
                                       ['all_order_count', all_order_count],
                                       ['win_order_count', win_order_count],
                                       ['loss_order_count', loss_order_count],
                                       ['equal_order_count', equal_order_count],
                                       ['win_order_count_ratio', win_order_count_ratio],
                                       ['loss_order_count_ratio', loss_order_count_ratio],
                                       ['equal_order_count_ratio', equal_order_count_ratio],
                                       ['win_orders_benefit', win_orders_benefit],
                                       ['loss_orders_benefit', loss_orders_benefit],
                                       ]]

        return result


if __name__ == '__main__':
    en_symbol_12_digit_code = 'IRO3PMRZ0001'
    tsetmc_id = '53449700212786324'

    # كشتيراني جمهوري اسلامي ايران (حكشتي)
    #en_symbol_12_digit_code = 'IRO1KSHJ0001'
    #tsetmc_id = '60610861509165508'


    # time info
    start_date_time = 20180101000000
    end_date_time = 20190511000000
    time_frame = 'D1'
    adjusted_mod = constant.adjusted_mod_now_time
    #adjusted_mod = constant.adjusted_mod_now_time
    adjusted_type = constant.adjusted_type_all
    #adjusted_type = constant.adjusted_type_none
    # adjusted_type = constant.adjusted_type_capital_increase
    # adjusted_type = constant.adjusted_type_all
    data_count = 0
    data_type = constant.ts_data_type_close

    max_benefit_up = 0.1
    max_benefit_down = 0.06

    order_total = 4
    order_same = 3

    strategy_variable = 'macd = MACD(26, 12, 9, self.bt_data)'
    strategy_context = '''
if macd.macd_line(0) > macd.signal_line(0):
    self.signal.buy()
elif macd.macd_line(0) < macd.signal_line(0):
    self.signal.sell()
else:
    self.signal.hold()'''

    strategy = (strategy_variable, strategy_context)

    output_format = ['analyze_strategy']

    app = App(strategy, output_format, start_date_time, end_date_time, time_frame, adjusted_type,
              max_benefit_up, max_benefit_down, order_total, order_same, data_type)

    #app.set_output_format_list(['test'])


    app.set_en_symbol_12_digit_code_list([en_symbol_12_digit_code])
    #app.add_output_format_list(['max_benefit'])
    res = app.run()
    print(res)
    #app.set_output_format_list(['back_test_benefit'])
    #app.run()

    print('----------')
    #old = False

    #start_time = datetime.now()
    #bt = BackTest(en_symbol_12_digit_code, start_date_time, end_date_time, time_frame, adjusted_type,
     #             max_benefit_up, max_benefit_down, order_total, order_same, data_type)

    #max_benefit_order_list = bt.get_max_benefit_order_list()
    #max_benefit_coeff = bt.get_max_benefit_profit()
    #print(max_benefit_order_list, max_benefit_coeff)#

    #print(bt.calc_backtest_benefit())
