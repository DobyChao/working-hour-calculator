import datetime
import json
import os
import time

# 设置json模板
JSON_TEMPLATE = {
    'total_working_time': 0,
    'total_working_days': 0,
    'lunch_time_start': None,
    'lunch_time_end': None,
    'dinner_time_start': None,
    'dinner_time_end': None,
    'working_days': []
}

WORKING_DAYS_TEMPLATE = {
    'date': None,
    'start_time': None,
    'end_time': None,
    'working_time': None
}

# 每天的开始和结束时间，以及午休或晚休时间
DAY_START = datetime.time(hour=0, minute=0)
DAY_END = datetime.time(hour=23, minute=59)

# 根据JSON文件创建数据类
class WorkHours:
    def __init__(self, json_file):
        self.json_file = json_file
        self.total_working_time = datetime.timedelta()
        self.total_working_days = 0
        self.lunch_time_start = None
        self.lunch_time_end = None
        self.dinner_time_start = None
        self.dinner_time_end = None
        self.working_days = []

        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                self.total_working_time = datetime.timedelta(seconds=data['total_working_time'])
                self.total_working_days = data['total_working_days']
                self.lunch_time_start = datetime.datetime.strptime(data['lunch_time_start'], '%H:%M').time()
                self.lunch_time_end = datetime.datetime.strptime(data['lunch_time_end'], '%H:%M').time()
                self.dinner_time_start = datetime.datetime.strptime(data['dinner_time_start'], '%H:%M').time()
                self.dinner_time_end = datetime.datetime.strptime(data['dinner_time_end'], '%H:%M').time()
                for working_day in data['working_days']:
                    self.working_days.append({
                        'date': datetime.datetime.strptime(working_day['date'], '%Y-%m-%d').date(),
                        'start_time': datetime.datetime.strptime(working_day['start_time'], '%H:%M:%S').time(),
                        'end_time': datetime.datetime.strptime(working_day['end_time'], '%H:%M:%S').time(),
                        'working_time': datetime.timedelta(seconds=working_day['working_time'])
                    })
        else:
            print(f'==================== 配置休息时间 ====================')
            self.set_rest_time()
            # 保存设置
            self.save()
            # 延时1秒
            time.sleep(1)
            # 清屏
            os.system('cls')
    
    def set_rest_time(self):
        print('请设置午休和晚休时间：')
        while self.lunch_time_start is None or self.lunch_time_end is None:
            lunch_time_str = input('请输入午休时间（格式为HH:MM-HH:MM）：')
            try:
                lunch_time_parts = lunch_time_str.split('-')
                self.lunch_time_start = datetime.datetime.strptime(lunch_time_parts[0], '%H:%M').time()
                self.lunch_time_end = datetime.datetime.strptime(lunch_time_parts[1], '%H:%M').time()
                if self.lunch_time_end < self.lunch_time_start:
                    raise ValueError('午休结束时间必须晚于开始时间')
                if self.lunch_time_start < DAY_START or self.lunch_time_end > DAY_END:
                    raise ValueError('午休时间必须在0:00到23:59之间')
            except ValueError as e:
                print('输入有误：', str(e))
                self.lunch_time_start = None
                self.lunch_time_end = None
        while self.dinner_time_start is None or self.dinner_time_end is None:
            dinner_time_str = input('请输入晚休时间（格式为HH:MM-HH:MM）：')
            try:
                dinner_time_parts = dinner_time_str.split('-')
                self.dinner_time_start = datetime.datetime.strptime(dinner_time_parts[0], '%H:%M').time()
                self.dinner_time_end = datetime.datetime.strptime(dinner_time_parts[1], '%H:%M').time()
                if self.dinner_time_end < self.dinner_time_start:
                    raise ValueError('晚休结束时间必须晚于开始时间')
                if self.dinner_time_start < DAY_START or self.dinner_time_end > DAY_END:
                    raise ValueError('晚休时间必须在0:00到23:59之间')
            except ValueError as e:
                print('输入有误：', str(e))
                self.dinner_time_start = None
                self.dinner_time_end = None

    def save(self):
        data = JSON_TEMPLATE.copy()
        data['total_working_time'] = self.total_working_time.total_seconds()
        data['total_working_days'] = self.total_working_days
        data['lunch_time_start'] = self.lunch_time_start.strftime('%H:%M')
        data['lunch_time_end'] = self.lunch_time_end.strftime('%H:%M')
        data['dinner_time_start'] = self.dinner_time_start.strftime('%H:%M')
        data['dinner_time_end'] = self.dinner_time_end.strftime('%H:%M')
        data['working_days'] = []
        for working_day in self.working_days:
            working_day_data = WORKING_DAYS_TEMPLATE.copy()
            working_day_data['date'] = working_day['date'].strftime('%Y-%m-%d')
            working_day_data['start_time'] = working_day['start_time'].strftime('%H:%M:%S')
            working_day_data['end_time'] = working_day['end_time'].strftime('%H:%M:%S')
            working_day_data['working_time'] = working_day['working_time'].total_seconds()
            data['working_days'].append(working_day_data)
        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=4)
        print('配置已保存在', self.json_file)
    
    def show(self, show_all=False):
        print('==================== 月工作时间统计 ====================')
        print('总工作时间：', self.total_working_time)
        print('总工作天数：', self.total_working_days)
        print('月平均工时：', self.total_working_time / self.total_working_days)
        if show_all:
            print('工作日：')
            for working_day in self.working_days:
                print(working_day['date'], working_day['start_time'].strftime('%H:%M:%S'), '-', working_day['end_time'].strftime('%H:%M:%S'), working_day['working_time'])

    def add_working_day(self, date, start_time, end_time):
        # 循环输入每天的起始时间和结束时间
        while True:
            print(f'==================== 配置{date}的工作时间 ====================')
            start_time_str = input('请输入开始时间（格式为HH:MM:SS）：')
            end_time_str = input('请输入结束时间（格式为HH:MM:SS）：')
            try:
                start_time = datetime.datetime.strptime(start_time_str, '%H:%M:%S').time()
                end_time = datetime.datetime.strptime(end_time_str, '%H:%M:%S').time()
                if end_time < start_time:
                    raise ValueError('结束时间必须晚于开始时间')
                if start_time < DAY_START or end_time > DAY_END:
                    raise ValueError('时间必须在0:00到23:59之间')
            except ValueError as e:
                print('输入有误：', str(e))
                continue
            
            # 计算工作时间
            start_datetime = datetime.datetime.combine(datetime.date.today(), start_time)
            end_datetime = datetime.datetime.combine(datetime.date.today(), end_time)
            working_time = end_datetime - start_datetime
            if start_time < self.lunch_time_end and end_time > self.lunch_time_start:
                if start_time < self.lunch_time_start:
                    if end_time < self.lunch_time_end:
                        working_time -= datetime.timedelta(seconds=(end_datetime - datetime.datetime.combine(datetime.date.today(), self.lunch_time_start)).seconds)
                    else:
                        working_time -= datetime.timedelta(seconds=(datetime.datetime.combine(datetime.date.today(), self.lunch_time_end) - datetime.datetime.combine(datetime.date.today(), self.lunch_time_start)).seconds)
                elif end_time > self.lunch_time_end:
                    working_time -= datetime.timedelta(seconds=(datetime.datetime.combine(datetime.date.today(), self.lunch_time_end) - start_datetime).seconds)
            if start_time < self.dinner_time_end and end_time > self.dinner_time_start:
                if start_time < self.dinner_time_start:
                    if end_time < self.dinner_time_end:
                        working_time -= datetime.timedelta(seconds=(end_datetime - datetime.datetime.combine(datetime.date.today(), self.dinner_time_start)).seconds)
                    else:
                        working_time -= datetime.timedelta(seconds=(datetime.datetime.combine(datetime.date.today(), self.dinner_time_end) - datetime.datetime.combine(datetime.date.today(), self.dinner_time_start)).seconds)
                elif end_time > self.dinner_time_end:
                    working_time -= datetime.timedelta(seconds=(datetime.datetime.combine(datetime.date.today(), self.dinner_time_end) - start_datetime).seconds)
            
            # 判断是否是新的一天
            def is_new_day(date):
                if len(self.working_days) == 0:
                    return True
                else:
                    return self.working_days[-1]['date'] != date
            
            date = datetime.date.today()
            # 如果是新的一天，添加新的一天
            if is_new_day(date):
                print('==================== 添加新的一天 ====================')
                self.working_days.append({
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'working_time': working_time
                })
                self.total_working_time += working_time
                self.total_working_days += 1
            else:
                print('==================== 更新最后一天 ====================')
                # 否则，更新最后一天的数据
                self.total_working_time -= self.working_days[-1]['working_time']
                self.working_days[-1]['start_time'] = start_time
                self.working_days[-1]['end_time'] = end_time
                self.working_days[-1]['working_time'] = working_time
                self.total_working_time += working_time

            break
        self.show()
        self.save()

if __name__ == "__main__":
    year_month = datetime.date.today().strftime('%Y-%m')
    save_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(save_dir, exist_ok=True)
    json_file = os.path.join(save_dir, year_month + '.json')
    work_hour_instance = WorkHours(json_file)
    while True:
        print('1. 添加工作日')
        print('2. 查看工作时间（简略）')
        print('3. 查看工作时间（详细）')
        print('0. 退出')
        choice = input('请输入选项：')
        if choice == '1':
            work_hour_instance.add_working_day(datetime.date.today(), datetime.time(9, 0, 0), datetime.time(18, 0, 0))
        elif choice == '2':
            work_hour_instance.show()
        elif choice == '3':
            work_hour_instance.show(show_all=True)
        elif choice == '0':
            break
        else:
            print('输入有误，请重新输入')
        
        # 按任意键继续
        os.system('pause')
        # 清屏
        os.system('cls')