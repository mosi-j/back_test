#import constant
from constant import constant

class base_indicator():
    def __init__(self):
        pass

    def sma(self, ts_data, period, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        if len(ts_data) < period:
            error = 'not enough data'
            if get_error is True:
                return None, error
            else:
                return None
        # ----------------------------
        #d = ts_data[0:candle_count]
        try:
            res = round(float(sum(ts_data[0:period])) / period, 2)
        except Exception as e:
            error = str(e)
            res = None

        # ----------------------------
        if get_error is True:
            return res, error
        else:
            return res
    def sma_list(self, ts_data, period, list_count, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        if list_count < 1:
            error = 'invalid list_count'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        sma_list = list()
        sum_p = sum(ts_data[0:period])
        for i in range(list_count):
            try:
                if i + period > len(ts_data):
                    error = 'not enough data'
                    res = None

                else:
                    if i == 0:
                        res = float(sum_p / period)
                        error = None

                    else:
                        sum_p = sum_p - ts_data[i - 1] + ts_data[i - 1 + period]
                        res = float(sum_p / period)
                        error = None

            except Exception as e:
                error = e
                res = None

            if get_error is True:
                sma_list.append([res, error])
            else:
                sma_list.append(res)

        if list_count == 1:
            sma_list = sma_list[0]
        # ----------------------------
        if get_error is True:
            return sma_list, error
        else:
            return sma_list

    def ema(self, ts_data, period, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        #if len(ts_data) < 2 * period:
        #    res = None
        #    error = 'not enough data'
        #    if get_error is True:
         #       return res, error
         #   else:
         #       return res

        # ----------------------------
        f = 2 / (period + 1)

        i = len(ts_data) - period
        ema, err = self.sma(ts_data[i:], period, True)
        if err is not None:
            error = err
            res = None
            if get_error is True:
                return res, error
            else:
                return res

        while i > 0:
            i -= 1
            if ema is None and i > period:
                ema, err = self.sma(ts_data[i:], period, True)
            elif ema is not None:
                try:
                    ema = ema * (1 - f) + ts_data[i] * f
                    err = None
                except Exception as e:
                    err = str(e)
                    ema = None

        error = err
        # ----------------------------
        if ema is None:
            r = None
        else:
            r = round(ema)

        if get_error is True:
            return r, error
        else:
            return r
    def ema_list(self, ts_data, period, list_count, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        if list_count < 1:
            error = 'invalid list_count'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        f = 2 / (period + 1)
        ema_list = list()
        i = len(ts_data) - period

        #ema = None
        #ema, err = self.sma(ts_data[i:], period, True)
        ema = None
        i += 1
        while i > 0:
            i -= 1
            if ema is None:
                ema, err = self.sma(ts_data[i:], period, True)
            else:
                try:
                    ema = ema * (1 - f) + ts_data[i] * f
                    err = None
                except Exception as e:
                    err = str(e)
                    ema = None

            #print(ema)
            if i < list_count:
                error = err
                if ema is None:
                    r = None
                else:
                    r = round(ema)
                if get_error is True:
                    ema_list.insert(0, [r, error])
                else:
                    ema_list.insert(0, r)

        while len(ema_list) < list_count:
            if get_error is True:
                error = 'not enough data'
                ema_list.append([None, error])
            else:
                ema_list.append(None)

        if list_count == 1:
            ema_list = ema_list[0]
        # ----------------------------
        if get_error is True:
            return ema_list, error
        else:
            return ema_list


    def smma(self, ts_data, period, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        if len(ts_data) < 2 * period:
            res = None
            error = 'not enough data'
            if get_error is True:
                return res, error
            else:
                return res

        # ----------------------------
        i = len(ts_data) - period
        smma, err = self.sma(ts_data[i:], period, True)

        while i > 0:
            i -= 1
            if smma is None and i > period:
                smma, err = self.sma(ts_data[i:], period, True)
            elif smma is not None:
                try:
                    smma = float(smma * (period - 1) + ts_data[i]) / period
                    err = None
                except Exception as e:
                    err = str(e)
                    smma = None

        # ----------------------------
        if smma is None:
            r = None
        else:
            r = round(smma, 2)

        error = err

        if get_error is True:
            return r, error
        else:
            return r
    def smma_list(self, ts_data, period, list_count, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        if list_count < 1:
            error = 'invalid list_count'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        smma_list = list()
        i = len(ts_data) - period
        #smma, err = self.sma(ts_data[i:], period, True)
        smma = None
        i += 1
        while i > 0:
            i -= 1
            if smma is None:
                smma, err = self.sma(ts_data[i:], period, True)
            else:
                try:
                    smma = float(smma * (period - 1) + ts_data[i]) / period
                    err = None
                except Exception as e:
                    err = str(e)
                    smma = None

            if i < list_count:
                if smma is None:
                    r = None
                else:
                    r = round(smma, 2)
                error = err

                if get_error is True:
                    smma_list.insert(0, [r, error])
                else:
                    smma_list.insert(0, r)

        while len(smma_list) < list_count:
            if get_error is True:
                error = 'not enough data'
                smma_list.append([None, error])
            else:
                smma_list.append(None)

        if list_count == 1:
            smma_list = smma_list[0]
        # ----------------------------
        if get_error is True:
            return smma_list, error
        else:
            return smma_list


    def lwma(self, ts_data, period, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        if len(ts_data) < period:
            res = None
            error = 'not enough data'
            if get_error is True:
                return res, error
            else:
                return res

        # ----------------------------
        sum = 0
        try:
            for i in range(period):
                sum += ts_data[i] * (period - i)
            lwma = float(sum / ((period + 1) * period / 2))
        except Exception as e:
            error = str(e)
            lwma = None
        # ----------------------------
        if lwma is None:
            r = None
        else:
            r = round(lwma, 2)
        #print('--' + str(ts_data[0]))
        if get_error is True:
            return r, error
        else:
            return r
    def lwma_list(self, ts_data, period, list_count, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        if list_count < 1:
            error = 'invalid list_count'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        lwma_list = list()
        i = len(ts_data) - period
        i += 1
        sum_p = None
        lwma = 0
        while i > 0:
            i -= 1
            if sum_p is None:
                try:
                    sum_p = 0
                    err = None
                    for j in range(period):
                        sum_p += ts_data[i + j] * (period - j)
                    lwma = float(sum_p / ((period + 1) * period / 2))

                except Exception as e:
                    err = str(e)
                    sum_p = None
            else:
                try:
                    sum_p = sum_p - sum(ts_data[i + 1:i + 1 + period]) + period * ts_data[i]
                    lwma = float(sum_p / ((period + 1) * period / 2))
                    err = None
                except Exception as e:
                    err = str(e)
                    sum_p = None
            # print(ema)
            if i < list_count:
                if sum_p is None:
                    r = None
                else:
                    r = round(lwma, 2)
                error = err
                if get_error is True:
                    lwma_list.insert(0, [r, error])
                else:
                    lwma_list.insert(0, r)

        while len(lwma_list) < list_count:
            if get_error is True:
                error = 'not enough data'
                lwma_list.append([None, error])
            else:
                lwma_list.append(None)

        if list_count == 1:
            lwma_list = lwma_list[0]
        # ----------------------------
        if get_error is True:
            return lwma_list, error
        else:
            return lwma_list


    def macd(self, ts_data, slow_period, fast_period, macd_period, get_error=False):
        error = None
        if slow_period < 1:
            error = 'invalid slow period'
            if get_error is True:
                return None, error
            else:
                return None

        if fast_period < 1:
            error = 'invalid fast period'
            if get_error is True:
                return None, error
            else:
                return None

        if macd_period < 1:
            error = 'invalid macd period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        #if len(ts_data) < (slow_period + macd_period) * 2:
        #    error = 'not enough data'
        #    if get_error is True:
        #        return None, error
        #    else:
        #        return None
        # ----------------------------
        macd_line_list = list()
        fast_point = None
        slow_point = None
        try:
            for i in range(len(ts_data)):
                slow = self.ema(ts_data[i:], slow_period)
                fast = self.ema(ts_data[i:], fast_period)
                if i == 0:
                    slow_point = slow
                    fast_point = fast

                if slow is None or fast is None:
                    break
                macd_line_list.append(fast - slow)

            macd_line = round(macd_line_list[0], 2)
            signal_line, err = self.ema(macd_line_list, macd_period, get_error=True)
            macd_histogram = round(macd_line - signal_line, 2)

            res = {'slow': slow_point, 'fast': fast_point, 'signal_line': signal_line,
                   'macd_line': macd_line, 'macd_histogram': macd_histogram}

        except Exception as e:
            error = str(e)
            res = {'slow': None, 'fast': None, 'signal_line': None, 'macd_line': None, 'macd_histogram': None}

        # ----------------------------
        if get_error is True:
            return res, error
        else:
            return res
    def macd_list(self, ts_data, slow_period, fast_period, macd_period, list_count, get_error=False):
        error = None
        if slow_period < 1:
            error = 'invalid slow period'
            if get_error is True:
                return None, error
            else:
                return None

        if fast_period < 1:
            error = 'invalid fast period'
            if get_error is True:
                return None, error
            else:
                return None

        if macd_period < 1:
            error = 'invalid macd period'
            if get_error is True:
                return None, error
            else:
                return None

        if list_count < 1:
            error = 'invalid list_count'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        macd_line_list = list()
        fast_list, fast_error = self.ema_list(ts_data, fast_period, len(ts_data), True)
        slow_list, slow_error = self.ema_list(ts_data, slow_period, len(ts_data), True)
        # macd_line_list = fast_list - slow_list
        macd_line_list =list()
        macd_line_list_data =list()
        for i in range(len(fast_list)):
            if fast_list[i][1] is not None:
                res_error = fast_list[i][1]
            elif slow_list[i][1] is not None:
                res_error = slow_list[i][1]
            else:
                res_error = None

            if fast_list[i][0] is None or slow_list[i][0] is None:
                res = None
            else:
                res = fast_list[i][0] - slow_list[i][0]
            macd_line_list.append([res, res_error])
            macd_line_list_data.append(res)



        #signal_line_list = self.ema_list(macd_line_list, macd_period, len(macd_line_list), False)
        signal_line_list, signal_line_list_error = self.ema_list(macd_line_list_data, macd_period, len(macd_line_list_data), True)
        #macd_histogram_list = list()
        res_list = list()

        #for i in range(len(signal_line_list)):
        for i in range(list_count):
            try:
                if signal_line_list[i][1] is not None:
                    res_error = signal_line_list[i][1]
                elif macd_line_list[i][1] is not None:
                    res_error = macd_line_list[i][1]
                else:
                    res_error = None

                res = {'slow': slow_list[i][0], 'fast': fast_list[i][0], 'signal_line': signal_line_list[i][0],
                   'macd_line': macd_line_list[i][0], 'macd_histogram': macd_line_list[i][0] - signal_line_list[i][0]}

            except Exception as e:
                res_error = str(e)
                res = {'slow': None, 'fast': None, 'signal_line': None, 'macd_line': None, 'macd_histogram': None}
            if get_error is True:
                res_list.append([res, res_error])
            else:
                res_list.append(res)

        if list_count == 1:
            res_list = res_list[0]
        # ----------------------------
        if get_error is True:
            return res_list, error
        else:
            return res_list


    def rsi(self, ts_data, period, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        if len(ts_data) < period + 1:
            error = 'not enough data'
            if get_error is True:
                return None, error
            else:
                return None
        # ----------------------------
        sum_gain = 0
        sum_loss = 0

        for i in range(period):
            a = ts_data[i] - ts_data[i + 1]
            if a > 0:
                sum_gain += a
            elif a < 0:
                sum_loss += a

        if sum_loss == 0:
            res = 100
        else:
            res = 100 - (100 / (1 + float(sum_gain / period) / float(-sum_loss / period)))

        # ----------------------------
        if get_error is True:
            return round(res, 2), error
        else:
            return round(res, 2)

    def williams(self, ts_data, period, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------------------
        if len(ts_data) < period:
            error = 'not enough data'
            if get_error is True:
                return None, error
            else:
                return None
        # ----------------------------
        hh = ts_data[0][constant.ts_field_high]
        ll = ts_data[0][constant.ts_field_low]
        for i in range(period):
            if ts_data[i][constant.ts_field_high] > hh:
                hh = ts_data[i][constant.ts_field_high]
            if ts_data[i][constant.ts_field_low] < ll:
                hh = ts_data[i][constant.ts_field_low]

        res = float((hh - ts_data[0][constant.ts_field_close]) / (hh - ll)) * -100

        # ----------------------------
        if get_error is True:
            return round(res, 2), error
        else:
            return round(res, 2)

    # ----------------------------------
    def sma_list0(self, ts_data, period, list_count, get_error=False):
        error = None
        if period < 1:
            error = 'invalid period'
            if get_error is True:
                return None, error
            else:
                return None

        if list_count < 1:
            error = 'invalid list_count'
            if get_error is True:
                return None, error
            else:
                return None

        # ----------------------------
        sma_list = list()
        rng = len(ts_data)
        for i in range(list_count):
            if i >= rng:
                res = None
                error = 'not enough data'
            else:
                res, error = self.sma(ts_data[i:], period, True)

            if get_error is True:
                sma_list.append([res, error])
            else:
                sma_list.append(res)

        if get_error is True:
            return sma_list, error
        else:
            return sma_list
