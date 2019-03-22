import time

import string

BASE_LIST = string.digits + string.ascii_lowercase + string.ascii_uppercase


class RegisterSN:
    """
    生成注册序列

    """
    school_code = '1000000001'

    def __init__(self):
        pass

    def get_serial_num(self, school_code=school_code):
        if school_code:
            self.school_code = school_code
        serial_num = "{}{}".format(self.school_code, int(time.time()))
        return int(serial_num)

    def get_bulk_sn(self, school_code=school_code):
        sn_list = []
        if school_code:
            self.school_code = school_code
        timestamp = int(time.time())
        for i in range(0, 10):
            serial_num = "{}{}".format(self.school_code, i + timestamp)
            sn_list.append(int(serial_num))
        return sn_list

    @classmethod
    def convert_to_base_x(cls, n, base):
        x, y = divmod(n, base)
        if x > 0:
            return cls.convert_to_base_x(x, base) + BASE_LIST[y]
        else:
            return BASE_LIST[y]


if __name__ == '__main__':
    rs = RegisterSN()
    sn = rs.get_serial_num()
    print(sn)
    bb = rs.convert_to_base_x(sn, 70)
    print(bb)
