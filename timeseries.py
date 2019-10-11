from new_database import Database
import datetime
from termcolor import colored
#import constant_database_data
#import constant
from constant_database_data import constant_database_data
from constant import constant


class TimeSeriesData:
    def __init__(self, database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                 time_frame, adjusted_mod, adjusted_type, data_count=0):
        self.db = Database(database_info, None)
        self.print_color = 'red'

        self.en_symbol_12_digit_code = en_symbol_12_digit_code
        self.end_date_time = end_date_time
        self.time_frame = time_frame
        self.adjusted_type = adjusted_type
        self.adjusted_mod = adjusted_mod
        self.start_date_time = start_date_time
        self.data_count = data_count

        self.no_any_data = False
        self.max_candle = 0
        # داد ها نزولی میباشند
        #self.all_adjusted_data, all_adjusted_data_error = self.__get_adjusted_coefficient_2(
        #    self.en_symbol_12_digit_code, self.start_date_time)

        # داد ها نزولی میباشند
        self.all_raw_second_data, all_raw_second_data_error = self.db.get_share_second_data(
            self.en_symbol_12_digit_code, self.start_date_time, self.end_date_time)

        if len(self.all_raw_second_data) == 0:
            self.no_any_data = True

        self.candle_date_list, candle_date_list_error = self.__get_candle_date_list(self.time_frame)

        self.origin_data_count = len(self.candle_date_list)
        self.max_candle = len(self.candle_date_list)

        self.last_adjusted_type = None
        self.all_raw_adjusted_data = None
        self.all_raw_adjusted_data_error = None
        self.__update_all_raw_adjusted_data()
        # self.all_raw_adjusted_data, all_raw_adjusted_data_error = self.__get_raw_adjusted_data()

        self.all_order_benefit_data, all_order_benefit_data_error = self.__get_order_benefit_data()

        if self.data_count > 0:
            res, error = self.__load_over_data(len(self.candle_date_list) - 1, self.data_count)
            if res is False:
                self.init_error = error
                return

    def print_c(self, text, color=None):
        try:
            if color is None:
                print(colored(text, self.print_color))
            else:
                print(colored('| ', self.print_color) + colored(text, color))
        except Exception as e:
            # self.__print_c(str(e), 'red')
            print(str(e))

    def __get_time(self, end_time, offset, time_frame):
            second = end_time % 100
            minute = int(end_time / 100) % 100
            hour = int(end_time / 10000) % 100
            day = int(end_time / 1000000) % 100
            month = int(end_time / 100000000) % 100
            year = int(end_time / 10000000000) % 10000

            r = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
            res = None

            if time_frame == 'S1':
                for i in range(round(offset)):
                    if r.hour == 9 and r.minute == 0 and r.second == 0:
                        r -= datetime.timedelta(days=1)
                        r = r.replace(hour=12, minute=29, second=59)
                    else:
                        r -= datetime.timedelta(seconds=1)
                res = r

            elif time_frame == 'M1':
                for i in range(round(offset)):
                    if i == 0 and second > 0:
                        r = r.replace(second=0)
                    else:
                        if r.hour == 9 and r.minute == 0:
                            r -= datetime.timedelta(days=1)
                            r = r.replace(hour=12, minute=29, second=0)
                        else:
                            r -= datetime.timedelta(minutes=1)
                res = r

            elif time_frame == 'H1':
                for i in range(round(offset)):
                    if i == 0 and (minute + second) > 0:
                        r = r.replace(minute=0, second=0)
                    else:
                        if r.hour > 9:
                            r -= datetime.timedelta(hours=1)
                        else:
                            r -= datetime.timedelta(hours=21)
                res = r

            elif time_frame == 'D1':
                for i in range(round(offset)):
                    if i == 0 and (hour + minute + second) > 0:
                        r = r.replace(hour=0, minute=0, second=0)
                    else:
                        r -= datetime.timedelta(days=1)
                res = r

            elif time_frame == 'MN1':
                for i in range(round(offset)):
                    if i == 0 and (day + hour + minute + second) > 1:
                        r = r.replace(day=1, hour=0, minute=0, second=0)
                    else:
                        y = r.year
                        m = r.month - 1
                        if m < 1:
                            m = 12
                            y -= 1
                            if y < 1:
                                break
                        r = r.replace(year=y, month=m)
                res = r

            elif time_frame == 'Y1':
                for i in range(round(offset)):
                    if i == 0 and (month + day + hour + minute + second) > 2:
                        r = r.replace(month=1, day=1, hour=0, minute=0, second=0)
                    else:
                        y = r.year - 1
                        if y < 1:
                            y = 1
                        r = r.replace(year=y)
                        if y == 1:
                            break
                res = r

            res = res.second + res.minute * 100 + res.hour * 10000 + res.day * 1000000 + \
                  res.month * 100000000 + res.year * 10000000000

            # self.__print_c(res, 'cyan')
            return res

    def __get_candle_date_list(self, time_frame):
        error = None
        candle_date_series = list()

        raw_data = self.all_raw_second_data
        # -----
        if len(raw_data) > 0:
            start_p1 = 0
            start_time_date = 0

            volume = 0
            start = True

            for item in raw_data:
                p1 = 0
                p1_time = p1

                if time_frame == 'S1':
                    p1 = item[0]
                    p1_time = p1

                elif time_frame == 'M1':
                    p1 = int(item[0] / 100)
                    p1_time = p1 * 100

                elif time_frame == 'H1':
                    p1 = int(item[0] / 10000)
                    p1_time = p1 * 10000

                elif time_frame == 'D1':
                    p1 = int(item[0] / 1000000)
                    p1_time = p1 * 1000000

                elif time_frame == 'MN1':
                    p1 = int(item[0] / 100000000)
                    # p1_time = p1 * 100000000
                    p1_time = p1 * 100000000 + 1000000


                elif time_frame == 'Y1':
                    p1 = int(item[0] / 10000000000)
                    p1_time = p1 * 10000000000

                if start is True:
                    start = False
                    volume = 1
                    start_p1 = p1
                    start_time_date = p1_time

                if p1 != start_p1:
                    candle_date_series.append(start_time_date)

                    # start new time frame
                    volume = 1
                    start_p1 = p1
                    start_time_date = p1_time

            if volume != 0:
                candle_date_series.append(start_time_date)

        return candle_date_series, error

    def __get_candle_data(self, candle_index, candle_count, adjusted_mod=None, adjusted_type=None):
        error = None
        res = True
        time_series = list()

        if candle_count < 1:
            res = time_series
            return res, error
        res, error = self.__load_over_data(candle_index, candle_count)

        if candle_index > self.max_candle:
            error = 'invalid candle back_test'
            res = False
            return res, error

        if candle_index == 0:
            end_index = 0
        else:
            end_date = self.candle_date_list[candle_index - 1]
            end_index = -1

            for i in range(len(self.all_raw_second_data)):
                # if self.all_raw_second_data[i][0] <= end_date:
                if self.all_raw_second_data[i][0] < end_date:
                    end_index = i
                    break
            if end_index == -1:
                error = 'back_test out of range'
                res = False
                return res , error

        source = self.all_raw_second_data[end_index:]
        coefficient_list, coefficient_list_error = self.get_adjusted_coefficient(
            int(self.candle_date_list[candle_index] / 1000000), adjusted_mod=adjusted_mod, adjusted_type=adjusted_type)
        # self.print_c( self.candle_date_list[back_test])
        # self.print_c( coefficient_list)
        # self.print_c( coefficient_list_error)

        if len(source) > 0:
            open = 0
            close = 0
            high = 0
            low = 0
            count = 0
            volume = 0
            value = 0
            start_p1 = 0
            start_time_date = 0

            start = True
            coefficient = 1
            coefficient_date = int(source[0][0] / 1000000)

            for item in source:
                p1 = 0
                p1_time = p1

                item_date = int(item[0] / 1000000)
                #if coefficient_date * 1000000 >= item[0]:
                if coefficient_date >= int(item[0] / 1000000):
                    for coeff in coefficient_list:
                        if coeff[0] < item_date :
                            coefficient_date = coeff[0]
                            break
                        coefficient = coeff[1]

                if self.time_frame == 'S1':
                    p1 = item[0]
                    p1_time = p1

                elif self.time_frame == 'M1':
                    p1 = int(item[0] / 100)
                    p1_time = p1 * 100

                elif self.time_frame == 'H1':
                    p1 = int(item[0] / 10000)
                    p1_time = p1 * 10000

                elif self.time_frame == 'D1':
                    p1 = int(item[0] / 1000000)
                    p1_time = p1 * 1000000

                elif self.time_frame == 'MN1':
                    p1 = int(item[0] / 100000000)
                    # p1_time = (p1 * 100 + 1) * 1000000
                    p1_time = p1 * 100000000 + 1000000

                elif self.time_frame == 'Y1':
                    p1 = int(item[0] / 10000000000)
                    p1_time = p1 * 10000000000

                if start is True:
                    start = False
                    open = item[1] * coefficient
                    close = item[2] * coefficient
                    high = item[3] * coefficient
                    low = item[4] * coefficient
                    volume = 0
                    value = 0
                    count = 0
                    start_p1 = p1
                    start_time_date = p1_time

                if p1 == start_p1:
                    open = item[1] * coefficient

                    if item[4] * coefficient < low:
                        low = item[4] * coefficient

                    if item[3] * coefficient > high:
                        high = item[4] * coefficient

                    count += item[5]
                    volume += item[6]
                    value += item[7]

                else:
                    # end = round(float(value) / volume)
                    time_series.append([start_time_date, int(open), int(close), int(high), int(low),
                                        volume, value, count])

                    if len(time_series) == candle_count:
                        volume = 0
                        break
                    # start new time frame
                    open = item[1] * coefficient
                    close = item[2] * coefficient
                    high = item[3] * coefficient
                    low = item[4] * coefficient
                    count = item[5]
                    volume = item[6]
                    value = item[7]

                    start_p1 = p1
                    start_time_date = p1_time

            if volume != 0:
                # end = round(float(value) / volume)
                time_series.append([start_time_date, int(open), int(close), int(high), int(low), volume, value, count])

            if len(time_series) == candle_count:
                error = None
                res = time_series

            elif self.no_any_data is True:
                error = 'no any data'
                res = time_series

            return res, error

    def __get_raw_adjusted_data(self, adjusted_type=None):
        if adjusted_type is None:
            adjusted_type = self.adjusted_type
        # return self.db.get_adjusted_data(self.en_symbol_12_digit_code, self.adjusted_type)
        return self.db.get_adjusted_data(self.en_symbol_12_digit_code, adjusted_type)

    def __update_all_raw_adjusted_data(self, adjusted_type=None):
        if adjusted_type is None:
            adjusted_type = self.adjusted_type

        if adjusted_type == self.last_adjusted_type:
            return True
        # self.all_raw_adjusted_data, all_raw_adjusted_data_error = self.__get_raw_adjusted_data(adjusted_type)
        self.all_raw_adjusted_data, all_raw_adjusted_data_error = self.db.get_adjusted_data(self.en_symbol_12_digit_code, adjusted_type)
        # print(self.all_raw_adjusted_data)
        # print(all_raw_adjusted_data_error)
        # print(adjusted_type)
        self.last_adjusted_type = adjusted_type
        # print(self.all_raw_adjusted_data)
        # print(self.all_raw_adjusted_data_error)
        # print(self.last_adjusted_type)

    def __get_order_benefit_data(self):
        res = list()
        raw_data, err = self.db.get_benefit_adjusted_data(self.en_symbol_12_digit_code)

        if err is not None:
            res = None
            return res, err

        for item in raw_data:
            if item[2] == constant.adjusted_type_capital_increase:
                res.append([item[0], item[1], 0])
            elif item[2] == constant.adjusted_type_take_profit:
                res.append([item[0], 1, item[3] - item[4]])

        # print(res)
        return res, err

    def __load_over_data(self, candle_index, candle_count):
        error = None
        res = True

        if self.no_any_data is True:
            error = 'no any data'
            return res, error

        end_date = self.candle_date_list[-1]
        i=0
        while candle_index + 1 + candle_count > len(self.candle_date_list):
            coeff = 2**i
            # need load any data
            now_candle_count = coeff * (candle_index + 1 + candle_count - len(self.candle_date_list))
            # self.print_c(now_candle_count)

            start_date = self.__get_time(end_date, now_candle_count, self.time_frame)
            add, add_error = self.db.get_share_second_data(self.en_symbol_12_digit_code, start_date, end_date)
            if add_error is not None:
                error = add_error
                res = False
                return res, error
            self.all_raw_second_data = self.all_raw_second_data + add
            self.candle_date_list, candle_date_list_error = self.__get_candle_date_list(self.time_frame)
            if candle_date_list_error is not None:
                error = candle_date_list_error
                res = False
                return res, error
            self.max_candle = len(self.candle_date_list)

            have_any_data , have_any_data_error = self.db.have_any_data(
                self.en_symbol_12_digit_code, self.candle_date_list[-1])
            if have_any_data_error is not None:
                error = add_error
                res = False
                return res, error

            if have_any_data is False:
                self.no_any_data = True
                error = 'no any data'
                res = True
                break

            end_date = start_date
            i += 1

        return res, error

    def get_adjusted_coefficient(self, end_date, adjusted_mod=None, adjusted_type=None):
        error = None
        res = list()
        coefficient = 1
        previous_coeff = None
        self.__update_all_raw_adjusted_data(adjusted_type)

        #start_date = 0
        if adjusted_mod is None:
            adjusted_mod = self.adjusted_mod

        if adjusted_mod == constant.adjusted_mod_off:
            return res, error

        elif adjusted_mod == constant.adjusted_mod_all_time:
            start_date = self.all_raw_adjusted_data[0][0] + 1

        elif adjusted_mod == constant.adjusted_mod_this_time:
            start_date = int(self.end_date_time / 1000000)

        elif adjusted_mod == constant.adjusted_mod_now_time:
            start_date = end_date
        else:
            res = False
            error = 'invalid adjusted mod'
            return res, error

        for coeff in self.all_raw_adjusted_data:
            if coeff[0] < start_date:
                coefficient *= coeff[1]

                if coeff[0] > end_date:
                    previous_coeff = [coeff[0], coefficient]

                elif coeff[0] == end_date:
                    res.append([coeff[0], coefficient])
                    previous_coeff = None

                else:
                    if previous_coeff is not None:
                        res.append(previous_coeff)
                        res.append([coeff[0], coefficient])
                        previous_coeff = None

                    else:
                        res.append([coeff[0], coefficient])

        if previous_coeff is not None:
            res.append(previous_coeff)

        # self.print_c(self.all_raw_adjusted_data)
        # self.print_c(res)
        return res, error

    def get_order_benefit_data(self):
        return self.all_order_benefit_data

    def get_candle_date(self, candle_index):
        if candle_index + 1 > self.origin_data_count:
            error = 'out off range day back_test'
            return False, error
        return self.candle_date_list[candle_index], None

    def get_candle_date_index(self, candle_date):
        res = None
        for i in range(len(self.candle_date_list)):
            if self.candle_date_list[i] == candle_date:
                res = i
                break
        return res

    def get_data(self, candle_index, candle_count, data_type=constant.ts_data_type_all, adjusted_mod = None, adjusted_type = None):
        res, err = self.__get_candle_data(candle_index, candle_count, adjusted_mod, adjusted_type)

        if err is not None:
            if err != 'no any data':
                return None, err

        if data_type == constant.ts_data_type_all:
            return res, err

        elif data_type == constant.ts_data_type_time:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_time])
            return result, err

        elif data_type == constant.ts_data_type_open:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_open])
            return result, err

        elif data_type == constant.ts_data_type_close:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_close])
            return result, err

        elif data_type == constant.ts_data_type_high:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_high])
            return result, err

        elif data_type == constant.ts_data_type_low:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_low])
            return result, err

        elif data_type == constant.ts_data_type_volume:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_volume])
            return result, err

        elif data_type == constant.ts_data_type_value:
            result = list()
            for item in res:
                result.append(item[constant.ts_field_value])
            return result, err

        elif data_type == constant.ts_data_type_median:
            result = list()
            for item in res:
                result.append((item[constant.ts_field_high] + item[constant.ts_field_low]) / 2)
            return result, err

        elif data_type == constant.ts_data_type_typical:
            result = list()
            for item in res:
                result.append((item[constant.ts_field_high] + item[constant.ts_field_low] +
                               item[constant.ts_field_close]) / 3)
            return result, err

        elif data_type == constant.ts_data_type_weighted:
            result = list()
            for item in res:
                result.append((item[constant.ts_field_high] + item[constant.ts_field_low] +
                               item[constant.ts_field_close]  + item[constant.ts_field_close])  / 4)
            return result, err

        else:
            return None, 'invalid data type'

    # -------
    def __get_candle_data00(self, candle_index, candle_count, adjusted_mod = None):
        error = None
        res = True
        time_series = list()

        if candle_count < 1:
            res = time_series
            return res, error

        res, error = self.__load_over_data(candle_index, candle_count)

        if candle_index > self.max_candle:
            error = 'invalid candle back_test'
            res = False
            return res, error

        if candle_index == 0:
            end_index = 0
        else:
            end_date = self.candle_date_list[candle_index - 1]
            end_index = -1

            for i in range(len(self.all_raw_second_data)):
                # if self.all_raw_second_data[i][0] <= end_date:
                if self.all_raw_second_data[i][0] < end_date:
                    end_index = i
                    break
            if end_index == -1:
                error = 'back_test out of range'
                res = False
                return res , error

        source = self.all_raw_second_data[end_index:]
        coefficient_list, coefficient_list_error = self.get_adjusted_coefficient(
            int(self.candle_date_list[candle_index] / 1000000), adjusted_mod)
        # self.print_c( self.candle_date_list[back_test])
        # self.print_c( coefficient_list)

        benefit_coefficient_list = list()
        for i in range(len(self.all_order_benefit_data)):
            if self.all_order_benefit_data[i][0] <= int(self.candle_date_list[candle_index] / 1000000):
                benefit_coefficient_list = self.all_order_benefit_data[i:]
                break

        if len(source) > 0:
            open = 0
            close = 0
            high = 0
            low = 0
            count = 0
            volume = 0
            value = 0
            start_p1 = 0
            start_time_date = 0

            start = True
            coefficient = 1
            coefficient_date = int(source[0][0] / 1000000)

            for item in source:
                p1 = 0
                p1_time = p1

                item_date = int(item[0] / 1000000)
                #if coefficient_date * 1000000 >= item[0]:
                #if coefficient_date >= int(item[0] / 1000000):
                #    for coeff in coefficient_list:
                #        if coeff[0] < item_date :
                #            coefficient_date = coeff[0]
                #            break
                #        coefficient = coeff[1]

                for i in range(len(benefit_coefficient_list)):
                    if benefit_coefficient_list[i][0] < item_date:
                        next_date = benefit_coefficient_list[i][0]
                        if i == 0:
                            coefficient_list = list()
                        else:
                            coefficient_list = benefit_coefficient_list[0:i]
                        break

                coeff = source[0][2]
                for row in coefficient_list:
                    print(coeff)
                    coeff = coeff / row[1] + row[2]

                coefficient = source[0][2] / coeff
                print(coefficient)


                if self.time_frame == 'S1':
                    p1 = item[0]
                    p1_time = p1

                elif self.time_frame == 'M1':
                    p1 = int(item[0] / 100)
                    p1_time = p1 * 100

                elif self.time_frame == 'H1':
                    p1 = int(item[0] / 10000)
                    p1_time = p1 * 10000

                elif self.time_frame == 'D1':
                    p1 = int(item[0] / 1000000)
                    p1_time = p1 * 1000000

                elif self.time_frame == 'MN1':
                    p1 = int(item[0] / 100000000)
                    # p1_time = (p1 * 100 + 1) * 1000000
                    p1_time = p1 * 100000000 + 1000000

                elif self.time_frame == 'Y1':
                    p1 = int(item[0] / 10000000000)
                    p1_time = p1 * 10000000000

                if start is True:
                    start = False
                    open = item[1] * coefficient
                    close = item[2] * coefficient
                    high = item[3] * coefficient
                    low = item[4] * coefficient
                    volume = 0
                    value = 0
                    count = 0
                    start_p1 = p1
                    start_time_date = p1_time

                if p1 == start_p1:
                    open = item[1] * coefficient

                    if item[4] * coefficient < low:
                        low = item[4] * coefficient

                    if item[3] * coefficient > high:
                        high = item[4] * coefficient

                    count += item[5]
                    volume += item[6]
                    value += item[7]

                else:
                    # end = round(float(value) / volume)
                    time_series.append([start_time_date, int(open), int(close), int(high), int(low),
                                        volume, value, count])

                    if len(time_series) == candle_count:
                        volume = 0
                        break
                    # start new time frame
                    open = item[1] * coefficient
                    close = item[2] * coefficient
                    high = item[3] * coefficient
                    low = item[4] * coefficient
                    count = item[5]
                    volume = item[6]
                    value = item[7]

                    start_p1 = p1
                    start_time_date = p1_time

            if volume != 0:
                # end = round(float(value) / volume)
                time_series.append([start_time_date, int(open), int(close), int(high), int(low), volume, value, count])

            if len(time_series) == candle_count:
                error = None
                res = time_series

            elif self.no_any_data is True:
                error = 'no any data'
                res = time_series

            return res, error

    def get_data10(self, candle_index, candle_count, data_type='all'):
        if data_type == 'all':
            return self.__get_candle_data(candle_index, candle_count)

        elif data_type == 'time':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_time])
            return result, err
        elif data_type == 'open':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_open])
            return result, err
        elif data_type == 'close':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_close])
            return result, err
        elif data_type == 'high':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_high])
            return result, err
        elif data_type == 'low':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_low])
            return result, err
        elif data_type == 'volume':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_volume])
            return result, err
        elif data_type == 'value':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append(item[constant.ts_field_value])
            return result, err
        # -------------------
        elif data_type == 'median':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append((item[constant.ts_field_high] + item[constant.ts_field_low]) / 2)
            return result, err
        # -------------------

        elif data_type == 'typical':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append((item[constant.ts_field_high] + item[constant.ts_field_low] +
                               item[constant.ts_field_close]) / 3)
            return result, err
        # -------------------

        elif data_type == 'weighted':
            res, err = self.__get_candle_data(candle_index, candle_count)
            if err is not None:
                return None, err

            result = list()
            for item in res:
                result.append((item[constant.ts_field_high] + item[constant.ts_field_low] +
                               item[constant.ts_field_close]  + item[constant.ts_field_close])  / 4)
            return result, err

        return None, 'invalid data type'

    # ---------------------


if __name__ == '__main__':
    # database_info = constant_database_data.pc1_server_role_db_info
    database_info = constant_database_data.laptop_analyze_server_role_db_info
    # پتروشيمي مارون
    en_symbol_12_digit_code = 'IRO3PMRZ0001'
    tsetmc_id = '53449700212786324'
    date_m = 20190610

    start_date_time = 20180610000000
    #start_date_time = 20120106000000
    end_date_time = 20190610000000
    #end_date_time = 20180825000000
    #end_date_time = 20180611000000

    time_frame = 'D1'
    adjusted_mod = constant.adjusted_mod_off
    data_count = 500

    ts_data = TimeSeriesData(database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                 time_frame, adjusted_mod, 1, data_count=data_count)

    day_index = 0
    list_len = 500

    d = ts_data.get_candle_date(day_index)

    ts_data.print_c(d)
    ts_data.print_c(ts_data.candle_date_list)

    ts_data.print_c(ts_data.no_any_data)


    print(ts_data.get_data(day_index, list_len))






    t=False
    if t:

        err = None
        res= ts_data.all_raw_adjusted_data
        ts_data.print_c('res:{0}  error:{1}'.format(res, err))
        ts_data.print_c('-----------------------------')

        res, err = ts_data.get_data(day_index, list_len)
        ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        # res, err = ts_data.get_adjusted_coefficient(int(end_date_time / 1000000))
        # ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        ts_data.print_c(1)
        #start_date_time = 20180610000000
        #end_date_time = 20180724000000
        #time_frame = 'D1'
        adjusted_mod = constant.adjusted_mod_all_time
        #data_count = 0

        ts_data2 = TimeSeriesData(database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                     time_frame, adjusted_mod, 1, data_count=data_count)

        res, err = ts_data2.get_data(day_index, list_len)
        ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        # res, err = ts_data2.get_adjusted_coefficient(int(end_date_time / 1000000))
        # ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        ts_data.print_c(2)
        #start_date_time = 20180610000000
        #end_date_time = 20180724000000
        #time_frame = 'D1'
        adjusted_mod = constant.adjusted_mod_now_time
        #data_count = 0

        ts_data3 = TimeSeriesData(database_info, en_symbol_12_digit_code, start_date_time, end_date_time,
                     time_frame, adjusted_mod, 1, data_count=data_count)

        res, err = ts_data3.get_data(day_index, list_len)
        ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        res = ts_data3.all_raw_adjusted_data
        ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        # res, err = ts_data3.get_adjusted_coefficient(int(end_date_time/1000000))
        # ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        # res, err = ts_data3.get_adjusted_coefficient(20170730)
        # ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        # res, err = ts_data3.get_adjusted_coefficient(20170930)
        # ts_data.print_c('res:{0}  error:{1}'.format(res, err))

        # res, err = ts_data3.get_adjusted_coefficient(10200930)
        # ts_data.print_c('res:{0}  error:{1}'.format(res, err))
        print(ts_data3.get_data(day_index, list_len))
        print(ts_data3.get_data(day_index, list_len, 'all'))
        print(ts_data3.get_data(day_index, list_len, 'open'))
        print(ts_data3.get_data(day_index, list_len, 'close'))
        print(ts_data3.get_data(day_index, list_len, 'high'))
        print(ts_data3.get_data(day_index, list_len, 'low'))
        #print(ts_data3.get_data(day_index, list_len, 'volume'))
        #print(ts_data3.get_data(day_index, list_len, 'value'))
        print(ts_data3.get_data(day_index, list_len, 'median'))
        print(ts_data3.get_data(day_index, list_len, 'typical'))
        print(ts_data3.get_data(day_index, list_len, 'weighted'))

        ts_data.print_c(3)

        # ---------------------------------------------------------------------
        database_info = constant_database_data.laptop_analyze_server_role_db_info
        en_symbol_12_digit_code = 'IRO3PMRZ0001'
        start_date_time = 20180410000000
        end_date_time = 20190611000000
        time_frame = 'D1'
        adjusted_mod = constant.adjusted_mod_off
        adjusted_type = constant.adjusted_type_capital_increase
        data_count = 2000

        series_data = TimeSeriesData(database_info, en_symbol_12_digit_code,
                                      start_date_time, end_date_time,
                                      time_frame, adjusted_mod, adjusted_type, data_count)

        index = 0
        data_type = constant.ts_data_type_close
        res = series_data.get_data(index, data_count, data_type)

        print(res)
        print(len(res[0]))