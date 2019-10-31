#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Time  : 2019/10/31 13:21
# @Author: Jtyoui@qq.com
from jtyoui.data import reader_conf
import time
import configparser
import os
import datetime
import re


class ParseTime:

    def __init__(self, data, current_date=None, date_format='%Y-%m-%d %H:%M:%S'):
        """初始化数据日期
        :param data:当前数据
        :param current_date:当前日期
        :param date_format:日期解析格式
        """
        # 加载日期的映射表和匹配日期的正则表
        self.map, self.re = None, None
        self.load_config()

        self.data = data
        # 定义当前日期
        self.localtime = current_date if current_date else time.strftime(date_format)

        self.format = date_format

        # 将当前日期标准化
        local = time.strptime(self.localtime, self.format)

        # 初始化当前的年月日基本信息
        self.now_year = local.tm_year
        self.now_mon = local.tm_mon
        self.now_day = local.tm_mday
        self.now_week = local.tm_wday + 1
        if current_date:
            self.now_hour = local.tm_hour
            self.now_minute = local.tm_min
            self.now_second = local.tm_sec
        else:
            self.now_hour = 0
            self.now_minute = 0
            self.now_second = 0

    def load_config(self, map_path=None, re_path=None):
        """自定义日期解析映射表和匹配日期的正则表
        :param map_path: 解析日期的映射表
        :param re_path: 匹配日期的正则表
        """
        path = os.path.dirname(__file__)
        self.map = configparser.ConfigParser()
        if map_path:
            self.map.read(map_path, encoding='UTF-8')
        else:
            self.map.read(path + os.sep + 'map.ini', encoding='UTF-8')
        if re_path:
            self.re = reader_conf(re_path)
        else:
            self.re = reader_conf(path + os.sep + 're.cfg')

    def change_time(self, day=0, hour=0, minute=0, week=0, second=0):
        """增加天数来修改时间"""
        add_time = datetime.timedelta(days=day, hours=hour, minutes=minute, weeks=week, seconds=second)
        add = datetime.datetime.strptime(self.str_time(), self.format) + add_time
        self.now_year = add.year
        self.now_mon = add.month
        self.now_day = add.day
        self.now_hour = add.hour
        self.now_minute = add.minute
        self.now_second = add.second
        self.now_week = add.isoweekday()

    def _analysis(self, name):
        """分析数据获取年月日周时分秒中的有效信息
        :param name: 年月日时周分秒调用名字
        :return: 改变的值
        """
        re_year = '|'.join(self.re['re_' + name])
        ls = re.search(re_year, self.data)
        if ls is not None:
            message = ls.group()
            add_year = self.map['add_' + name]
            value = add_year.get(message, 0)
        else:
            value = 0
        return int(value)

    def standard_time(self):
        """标准时间化"""
        return time.strptime(self.str_time(), self.format)

    def str_time(self):
        """字符串时间"""
        return self.__str__()

    def day(self):
        """查询天数"""
        value = self._analysis('day')
        self.change_time(day=value)

    def month(self):
        """查询月份"""
        value = self._analysis('month')
        mon = self.now_mon + value
        if mon == 0:
            self.now_year -= 1
            mon = 12
        if mon > 12:
            over_12_mon, mod_12 = divmod(mon, 12)
            self.now_year += over_12_mon
            self.now_mon = mod_12
        else:
            self.now_mon = mon

    def year(self):
        """查询年份"""
        value = self._analysis('year')
        self.now_year += value

    def week(self):
        value = self._analysis('week')
        self.change_time(week=value)

    def what_week(self):
        ds = self.map['chinese_mon']
        keys = r'星期(\d+|' + '|'.join(ds.keys())[4:-11] + '天|日)'
        match = re.search(keys, self.data)
        if match is not None:
            value = match.group()
            point = value[2:]
            if point.isdigit():
                w = int(point)
            elif ds.get(point, None) is not None:
                w = int(ds[point])
            elif point in '天日':
                w = 7
            else:
                w = self.now_week  # 暂未设置
            differ = w - self.now_week
            self.change_time(day=differ)

    def hour(self):
        re_hour = '(' + '|'.join(self.re['re_hour']) + ')' + r'\d+点'
        match = re.search(re_hour, self.data)
        if match is not None:
            value = match.group()
            add_hour = int(value[2:-1])
            point = value[:2]
            sc = int(self.map['add_hour'].get(point, 0))
            if add_hour < sc:
                add_hour += sc
            self.change_time(hour=add_hour)

    def minute(self):
        re_minute = '|'.join(self.re['re_minute'])
        match = re.search(re_minute, self.data)
        if match is not None:
            value = match.group()
            if '点半' in value:
                add_min = 30
            elif '分' in value:
                add_min = int(value[:-1])
            else:
                add_min = 0  # 其他情况
            self.change_time(minute=add_min)

    def second(self):
        re_second = '|'.join(self.re['re_second'])
        match = re.search(re_second, self.data)
        if match is not None:
            value = match.group()
            if '秒' in value:
                add_second = int(value[:-1])
                self.change_time(second=add_second)

    def parse(self):
        self.second()
        self.minute()
        self.hour()
        self.week()
        self.what_week()
        self.day()
        self.month()
        self.year()
        return self.standard_time()

    def __add__(self, other):
        pass

    def __iadd__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __imul__(self, other):
        pass

    def __str__(self):
        return F'{self.now_year}-{self.now_mon}-{self.now_day} ' \
               F'{self.now_hour:0>2}:{self.now_minute:0>2}:{self.now_second:0>2}'

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    pt = ParseTime('上上个周星期天下午2点25分钟30秒')
    t = pt.parse()
    print(pt)