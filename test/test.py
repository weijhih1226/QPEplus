# -*- coding: utf-8 -*-

import csv
import os , sys
import argparse
import datetime as dt
from datetime import datetime as dtdt
from pydantic.main import BaseModel

# 中文編碼

class MyArgs(BaseModel):
    test1: int
    test2: int
    test3: int
    test4: bool = False
    test5: bool = False

def main(*args):
    # args = args[1:]
    # print(args)
    # args = sys.argv[1:]
    print(args)
    parser = argparse.ArgumentParser(prefix_chars='+')
    parser.add_argument('test1' , help='test1')
    parser.add_argument('test2' , help='test2')
    parser.add_argument('test3' , help='test3')
    parser.add_argument('test4' , action = 'store_false' , default = False , help='test4')
    parser.add_argument('test5' , action = 'store_false' , default = False , help='test5')
    parsed_arg = parser.parse_args(args)
    print(*args)
    print(parsed_arg)
    print(type(parsed_arg))
    parsed_arg = MyArgs(**parsed_arg.__dict__)

    print(parsed_arg.test1)

    datetime_start = dtdt.strptime('2022/05/20 00:00:00' , '%Y/%m/%d %H:%M:%S').timestamp()
    datetime_end = (dtdt.now() - dt.timedelta(minutes = 10)).timestamp()
    print(int((datetime_end - datetime_start) / 60))
    print(sys.path)

    print(not(os.listdir(fr'C:\Users\wjchen\Documents\Qplus\test')))

    inPath = rf'C:\Users\wjchen\Documents\個案挑選\case_time.csv'
    with open(inPath , newline = '' , encoding = 'utf-8') as fi:
        data = csv.reader(fi)
        next(data)
        for row in data:
            print(row[0] , row[1] , row[2])

if __name__ == '__main__':
    main(*sys.argv[1:])