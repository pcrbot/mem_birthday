import os 
import yaml
import datetime

# 获取时间
async def get_time():
    today = datetime.datetime.now()
    dat = datetime.date(today.year,today.month,today.day)
    return dat

# 获取星期
async def get_week_day(date):
    week_day = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期日',
    }
    day = date.weekday()
    return week_day[day]

# 祝贺这几个B生日快乐
async def get_bir_info(bir_list):
    tod = await get_time()
    week_day = await get_week_day(tod)
    msg = f'今天是 {str(tod)} {week_day}\n\n让我们祝贺这{len(bir_list)}个群友生日快乐：'
    for user_id in bir_list:
        msg += f'\n[CQ:at,qq={user_id}]'
    msg += '\n这是小蛋糕：[CQ:face,id=53][CQ:face,id=53][CQ:face,id=53]'
    return msg

# 判断是否生日
async def judge_bir(gid):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(current_dir, 'r', encoding="UTF-8") as f:
        file_data = f.read()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    bir_list = []
    for user in config['Info'][gid]:
        user_id = int(user['member']['user_id'])
        yes_age = int(user['member']['yes_age'])
        tod_age = int(user['member']['tod_age'])
        if tod_age == yes_age + 1:
            # 这说明这个B生日了
            bir_list.append(user_id)
    return bir_list