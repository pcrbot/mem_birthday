import os 
import yaml
import asyncio

import hoshino

# 首次启动时，若没有`config.yml`则创建配置文件
async def init_info(bot, glist_info):
    _current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    if not os.path.exists(_current_dir):
        hoshino.logger.info('所有群的群成员信息正在初始化中，请耐心等待...')
        await create_yml(bot, _current_dir, glist_info)
        hoshino.logger.info('群成员生日信息初始化成功')
        msg = '群员生日初始化成功'
    else:
        msg = '您已经初始化过了！无需再次初始化'
    return msg

# 创建Data，并加入群组数据
async def create_yml(bot, _current_dir, glist_info):
    data = {'Info': {}}
    for each_g in glist_info:
        await asyncio.sleep(1)
        group_id = each_g['group_id']
        hoshino.logger.info(f'开始更新群{group_id}的群员生日')
        data['Info'].setdefault(group_id,[])
        group_info = await bot.get_group_member_list(group_id = group_id, no_cache = True)
        for each_mem in group_info:
            await asyncio.sleep(1)
            uid = int(each_mem['user_id'])
            # 这个区间的几个B是QQ自己的机器人，不会有人还用这个机器人吧
            if uid >= 2854196300 and uid <= 2854196399:
                continue
            mem_info = await bot.get_stranger_info(user_id = uid, no_cache = True)
            age = int(mem_info['age'])
            mem_data = {
                'member':{
                    'user_id': uid,
                    'yes_age': age, 
                    'tod_age': age
                }
            }
            data['Info'][group_id].append(mem_data)
        hoshino.logger.info(f'群{group_id}的群员生日更新完成！')
    with open(_current_dir, "w", encoding="UTF-8") as f:
        yaml.dump(data, f,allow_unicode=True)