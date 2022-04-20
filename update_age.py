import os 
import yaml
import asyncio

import hoshino

# 获取文件中的数据并删除旧版数据
async def get_tod(gid, uid):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(current_dir, 'r', encoding="UTF-8") as f:
        file_data = f.read()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    config, flag = await judge_newer(config, uid, gid)
    # 新群员或新群
    if flag == 1:
        tod_age = -1
        return current_dir, config, tod_age, flag
    tod_age = 0
    for user in config['Info'][gid]:
        user_id = int(user['member']['user_id'])
        if user_id == uid:
            yes_age = int(user['member']['yes_age'])
            tod_age = int(user['member']['tod_age'])
            mem_data = {
                'member':{
                    'user_id': uid,
                    'yes_age': yes_age, 
                    'tod_age': tod_age
                }
            }
            config['Info'][gid].remove(mem_data)
    return current_dir, config, tod_age, flag

# 写入新的数据，将tod_age移到yes_age
async def repalce_age(bot, glist_info):
    for each_g in glist_info:
        await asyncio.sleep(1)
        gid = each_g['group_id']
        hoshino.logger.info(f'开始更新群{gid}的群员生日')
        group_info = await bot.get_group_member_list(group_id = gid, no_cache = True)
        for each_mem in group_info:
            await asyncio.sleep(1)
            uid = int(each_mem['user_id'])
            # 这个区间的几个B是QQ自己的机器人，不会有人还用这个机器人吧
            if uid >= 2854196300 and uid <= 2854196399:
                continue
            current_dir, config, tod_age, flag = await get_tod(gid, uid)
            mem_info = await bot.get_stranger_info(user_id = uid, no_cache = True)
            age = int(mem_info['age'])
            yes_age = age if flag == 1 else tod_age
            mem_data = {
                'member':{
                    'user_id': uid,
                    'yes_age': yes_age,
                    'tod_age': age
                }
            }
            config['Info'][gid].append(mem_data)
            with open(current_dir, "w", encoding="UTF-8") as f:
                yaml.dump(config, f,allow_unicode=True)
        hoshino.logger.info(f'群{gid}的群员生日更新完成！')

# 判断更新数据时，是否有新群员或者新群
async def judge_newer(config, uid, gid):
    # 判断是否是新加入的群，是则也是新群员
    flag = 1
    if gid not in list(config['Info'].keys()):
        config['Info'].setdefault(gid,[])
    else:
        # 判断群存在的时候是否是新群员
        for user in config['Info'][gid]:
            user_id = int(user['member']['user_id'])
            if user_id == uid:
                flag = 0
    return config, flag

# 退群删信息
async def del_mem(current_dir, gid, uid):
    with open(current_dir, 'r', encoding="UTF-8") as f:
        file_data = f.read()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    for mem in config['Info'][gid]:
        if int(mem['member']['user_id']) == uid:
            config['Info'][gid].remove(mem)
    with open(current_dir, "w", encoding="UTF-8") as f:
        yaml.dump(config, f,allow_unicode=True)