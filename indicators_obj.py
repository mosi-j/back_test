
from base_inducarots import base_indicator
#import constant
from constant import constant
# from back_test import BackTest_Data

over_coeff = 10

class Data():
    def __init__(self, bt_data):
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data

    def get_data(self, candle_index, candle_count=1, data_type=None, get_error=False):
        # if data_type is None:
        #    data_type = self.bt_data.get_default_data_type()

        res, error = self.bt_data.get_data(candle_index, candle_count, data_type)

        #print(error)
        if candle_count == 1:
            if res is not None:
                res = res[0]

        if get_error is True:
            return res, error
        else:
            return res


class SMA(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # if data_type is None:
        #    data_type = self.bt_data.get_default_data_type()
        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, self.period, data_type)
        if error is not None:
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------
        return self.sma(res, self.period, get_error)


class SMA_list(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, list_count, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # if data_type is None:
        #    data_type = self.bt_data.get_default_data_type()
        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, self.period + list_count, data_type)
        if error is not None:
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------
        return self.sma_list(res, self.period, list_count, get_error)


class EMA(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        # coeff = 1.5
        coeff = over_coeff
        res, error = self.bt_data.get_data(candle_index, round((2 + coeff) * self.period), data_type)

        # ----------------------------
        if len(res) < 2 * self.period:
            res = None
            error = 'not enough data'
            if get_error is True:
                return res, error
            else:
                return res

        # ----------------------------
        return self.ema(res, self.period, get_error)


class EMA_list(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, list_count, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        # coeff = 1.5
        coeff = over_coeff
        res, error = self.bt_data.get_data(candle_index, round((2 + coeff) * self.period) + list_count, data_type)

        # ----------------------------
        return self.ema_list(res, self.period, list_count, get_error)


class SMMA(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        # coeff = 0.5
        coeff = over_coeff

        res, error = self.bt_data.get_data(candle_index, round((2 + coeff) * self.period), data_type)

        # ----------------------------
        if len(res) < 2 * self.period:
            res = None
            error = 'not enough data'
            if get_error is True:
                return res, error
            else:
                return res

        # ----------------------------
        return self.smma(res, self.period, get_error)


class SMMA_list(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, list_count, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        # coeff = 1.5
        coeff = over_coeff
        res, error = self.bt_data.get_data(candle_index, round((2 + coeff) * self.period) + list_count, data_type)

        # ----------------------------
        return self.smma_list(res, self.period, list_count, get_error)


class LWMA(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # if data_type is None:
        #   data_type = self.bt_data.get_default_data_type()
        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, self.period, data_type)
        if error is not None:
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------
        return self.lwma(res, self.period, get_error)


class LWMA_list(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, list_count, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, self.period + list_count, data_type)
        # ----------------------------
        return self.lwma_list(res, self.period, list_count, get_error)


class MACD(base_indicator):
    def __init__(self, slow_period, fast_period, macd_period, bt_data):
        self.obj_error = None
        self.slow_period = slow_period
        self.fast_period = fast_period
        self.macd_period = macd_period
        # self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

        self.last_base_index = None
        self.last_candle_index = None
        self.last_data_type = None
        self.last_get_error = None
        self.last_data = None
        self.last_error = None

    def d(self, candle_index, data_type=None, get_error=False):
        current_base_index = self.bt_data.get_base_index()
        if self.last_data is not None:
            if self.last_base_index == current_base_index and self.last_candle_index == candle_index and self.last_data_type == data_type and self.last_get_error == get_error:
                if get_error is True:
                    return self.last_data, self.last_error
                else:
                    return self.last_data

        if self.slow_period < 1:
            error = 'invalid slow period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.fast_period < 1:
            error = 'invalid fast period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.macd_period < 1:
            error = 'invalid macd period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, 10 * (self.slow_period + self.macd_period), data_type)
        # ---------------------------
        error = None
        if get_error is True:
            res, error = self.macd(res, self.slow_period, self.fast_period, self.macd_period, get_error)
        else:
            res = self.macd(res, self.slow_period, self.fast_period, self.macd_period, get_error)
        # ----------------------------
        self.last_base_index = current_base_index
        self.last_candle_index = candle_index
        self.last_data_type = data_type
        self.last_get_error = get_error
        self.last_data = res
        self.last_error = error

        if get_error is True:
            return res, error
        else:
            return res

    def slow(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            d_res, error = self.d(candle_index, data_type, get_error)
        else:
            d_res = self.d(candle_index, data_type, get_error)

        try:
            res = d_res['slow']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def fast(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            d_res, error = self.d(candle_index, data_type, get_error)
        else:
            d_res = self.d(candle_index, data_type, get_error)

        try:
            res = d_res['fast']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def signal_line(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            d_res, error = self.d(candle_index, data_type, get_error)
        else:
            d_res = self.d(candle_index, data_type, get_error)

        try:
            res = d_res['signal_line']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def macd_line(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            d_res, error = self.d(candle_index, data_type, get_error)
        else:
            d_res = self.d(candle_index, data_type, get_error)

        try:
            res = d_res['macd_line']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def macd_histogram(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            d_res, error = self.d(candle_index, data_type, get_error)
        else:
            d_res = self.d(candle_index, data_type, get_error)

        try:
            res = d_res['macd_histogram']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res


class MACD0(base_indicator):
    def __init__(self, slow_period, fast_period, macd_period, bt_data):
        self.obj_error = None
        self.slow_period = slow_period
        self.fast_period = fast_period
        self.macd_period = macd_period
        # self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.slow_period < 1:
            error = 'invalid slow period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.fast_period < 1:
            error = 'invalid fast period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.macd_period < 1:
            error = 'invalid macd period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, 10 * (self.slow_period + self.macd_period), data_type)
        # ----------------------------
        return self.macd(res, self.slow_period, self.fast_period, self.macd_period, get_error)

    def slow(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            res, error = self.d(candle_index, data_type, get_error)
        else:
            res = self.d(candle_index, data_type, get_error)

        try:
            res = res['slow']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def fast(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            res, error = self.d(candle_index, data_type, get_error)
        else:
            res = self.d(candle_index, data_type, get_error)

        try:
            res = res['fast']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def signal_line(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            res, error = self.d(candle_index, data_type, get_error)
        else:
            res = self.d(candle_index, data_type, get_error)

        try:
            res = res['signal_line']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def macd_line(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            res, error = self.d(candle_index, data_type, get_error)
        else:
            res = self.d(candle_index, data_type, get_error)

        try:
            res = res['macd_line']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res

    def macd_histogram(self, candle_index, data_type=None, get_error=False):
        error = None
        if get_error is True:
            res, error = self.d(candle_index, data_type, get_error)
        else:
            res = self.d(candle_index, data_type, get_error)

        try:
            res = res['macd_histogram']
        except:
            res = None

        if get_error is True:
            return res, error
        else:
            return res


class MACD_list(base_indicator):
    def __init__(self, slow_period, fast_period, macd_period, bt_data):
        self.obj_error = None
        self.slow_period = slow_period
        self.fast_period = fast_period
        self.macd_period = macd_period
        # self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

        self.last_base_index = None
        self.last_candle_index = None
        self.last_data_type = None
        self.last_get_error = None
        self.last_data = None
        self.last_error = None

    def d(self, candle_index, list_count, data_type=None, get_error=False):
        current_base_index = self.bt_data.get_base_index()
        if self.last_data is not None:
            if self.last_base_index == current_base_index and self.last_candle_index == candle_index and self.last_data_type == data_type and self.last_get_error == get_error:
                if list_count <= len(self.last_data):
                    if get_error is True:
                        return self.last_data[:list_count], self.last_error
                    else:
                        return self.last_data[:list_count]

        if self.slow_period < 1:
            error = 'invalid slow period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.fast_period < 1:
            error = 'invalid fast period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.macd_period < 1:
            error = 'invalid macd period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, 3 * (self.slow_period + self.macd_period) + list_count, data_type)
        # ----------------------------
        # ---------------------------
        error = None
        if get_error is True:
            res, error = self.macd_list(res, self.slow_period, self.fast_period, self.macd_period, list_count, get_error)
        else:
            res = self.macd_list(res, self.slow_period, self.fast_period, self.macd_period, list_count, get_error)
        # ----------------------------
        self.last_base_index = current_base_index
        self.last_candle_index = candle_index
        self.last_data_type = data_type
        self.last_get_error = get_error
        self.last_data = res
        self.last_error = error

        if get_error is True:
            return res, error
        else:
            return res

    def slow(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['slow'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['slow'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def fast(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['fast'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['fast'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def signal_line(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['signal_line'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['signal_line'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def macd_line(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['macd_line'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['macd_line'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def macd_histogram(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['macd_histogram'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['macd_histogram'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list


class MACD_list0(base_indicator):
    def __init__(self, slow_period, fast_period, macd_period, bt_data):
        self.obj_error = None
        self.slow_period = slow_period
        self.fast_period = fast_period
        self.macd_period = macd_period
        # self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, list_count, data_type=None, get_error=False):
        if self.slow_period < 1:
            error = 'invalid slow period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.fast_period < 1:
            error = 'invalid fast period'
            if get_error is True:
                return None, error
            else:
                return None

        if self.macd_period < 1:
            error = 'invalid macd period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, 3 * (self.slow_period + self.macd_period) + list_count, data_type)
        # ----------------------------
        return self.macd_list(res, self.slow_period, self.fast_period, self.macd_period, list_count, get_error)

    def slow(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['slow'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['slow'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def fast(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['fast'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['fast'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def signal_line(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['signal_line'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['signal_line'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def macd_line(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['macd_line'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['macd_line'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list

    def macd_histogram(self, candle_index, list_count, data_type=None, get_error=False):
        res, error = self.d(candle_index, list_count + 1, data_type, True)
        res = res[:-1]

        res_list = list()
        for i in range(len(res)):
            if get_error is True:
                try:
                    res_list.append([res[i][0]['macd_histogram'], res[i][1]])
                except Exception as e:
                    res_list.append([None, str(res[i][1]) + ' : ' + str(e)])
            else:
                try:
                    res_list.append(res[i][0]['macd_histogram'])
                except:
                    res_list.append(None)

        if get_error is True:
            return res_list, error
        else:
            return res_list


class RSI(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # if data_type is None:
        #    data_type = self.bt_data.get_default_data_type()
        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, self.period + 1, data_type)
        if error is not None:
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------
        return self.rsi(res, self.period, get_error)


class WILLIAMS(base_indicator):
    def __init__(self, period, bt_data):
        self.obj_error = None
        self.period = period
        #self.bt_data:BackTest_Data = bt_data
        self.bt_data = bt_data
        base_indicator.__init__(self)

    def d(self, candle_index, data_type=None, get_error=False):
        if self.period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # if data_type is None:
        #    data_type = self.bt_data.get_default_data_type()
        # ----------------------------------------
        res, error = self.bt_data.get_data(candle_index, self.period + 1, data_type=constant.ts_data_type_all)
        if error is not None:
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------
        return self.williams(res, self.period, get_error)
