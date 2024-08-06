import time


class TimeUtil:
    @staticmethod
    def now():
        return int(time.time() * 1000)

    @staticmethod
    def current_time(types='%Y-%m-%d %H:%M:%S'):
        """
        返回当前日期和时间
        :return:
        """
        return time.strftime(types, time.localtime(time.time()))

    def second_stamp(self, times, types="%Y-%m-%d %H:%M:%S"):
        """
        时间->秒,转换为时间戳
        :return:
        """
        st = time.strptime(times, types)
        st = int(time.mktime(st))
        return st


if __name__ == '__main__':
    print(TimeUtil.now())