#import constant
from constant import constant

class buy_sell_opt():
    def __init__(self, option):
        try:
            self.series_data = option['series_data_obj']
            self.current_candle_index = option['current_candle_index']
            self.option = option
        except Exception as e:
            obj_error = e
        self.output_list = list()

    def sell(self):
        candle_date = self.series_data.get_candle_date(self.option['current_candle_index'])
        close_price = self.series_data.get_data(self, self.option['current_candle_index'], 1,
                                                data_type=constant.ts_data_type_close)
        self.output_list.append([candle_date, close_price, 'sell'])

    def buy(self):
        candle_date = self.series_data.get_candle_date(self.option['current_candle_index'])
        close_price = self.series_data.get_data(self, self.option['current_candle_index'], 1,
                                                data_type=constant.ts_data_type_close)
        self.output_list.append([candle_date, close_price, 'buy'])

    def hold(self):
        candle_date = self.series_data.get_candle_date(self.option['current_candle_index'])
        close_price = self.series_data.get_data(self, self.option['current_candle_index'], 1,
                                                data_type=constant.ts_data_type_close)
        self.output_list.append([candle_date, close_price, 'hold'])

    def output(self):
        return self.output_list
