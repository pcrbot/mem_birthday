import os
import asyncio

import hoshino
from hoshino import Service, priv
from hoshino.typing import NoticeSession
from .create_config import *
from .comp_birth import *
from .update_age import *

sv = Service('member_birthday', help_='每天早上8点推送祝福当天生日群友', enable_on_default=True)

current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')

# 初始化
@sv.on_fullmatch('群员生日初始化')
async def init_birth(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.finish(ev, msg)
    await bot.send(ev, '正在开始初始化群员生日配置...')
    glist_info = await bot.get_group_list()
    msg = await init_info(bot, glist_info)
    await bot.send(ev, msg)

# 推送生日祝福
@sv.scheduled_job('cron', hour='8', minute='00') # 早上8点推送祝福，让你在赶着上班上学的同时得到一丝温馨感（
async def auto_compare():
    if not os.path.exists(current_dir):
        hoshino.logger.error('未初始化过群员生日，因此无法推送生日')
        return
    bot = hoshino.get_bot()
    glist_info = await sv.get_enable_groups()
    for gid in glist_info:
        await asyncio.sleep(5)
        bir_list = await judge_bir(gid)
        if bir_list:
            sv.logger.info(f'检测到今天群号{gid}里有{len(bir_list)}位群友生日！')
            msg = await get_bir_info(bir_list)
            await bot.send_group_msg(group_id=gid, message=msg)
        else:
            sv.logger.info(f'今天群号{gid}里没有群友生日欸~')

# 更新每天的年龄
@sv.scheduled_job('cron', hour='1', minute='00') # 凌晨两点更新数据
async def auto_update():
    if not os.path.exists(current_dir):
        hoshino.logger.error('未初始化过群员生日，因此无法更新生日')
        return
    bot = hoshino.get_bot()
    superid = hoshino.config.SUPERUSERS[0]
    sv.logger.info('正在更新群友信息...预计用时几分钟')
    try:
        glist_info = await bot.get_group_list()
        await repalce_age(bot, glist_info)
        sv.logger.info('所有群友年龄信息更新完成')
    except Exception as e:
        msg ='所有群友年龄信息更新失败：' + str(e)
        sv.logger.error(msg)
        await bot.send_private_msg(user_id=superid, message=msg)

# 测试用的
@sv.on_fullmatch('手动更新群员生日')
async def update_bir(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.finish(ev, msg)
    if not os.path.exists(current_dir):
        await bot.finish(ev, '您还未初始化过呢！')
    msg = '正在手动更新数据中...'
    await bot.send(ev, msg)
    sv.logger.info('正在更新群友信息...预计用时几分钟')
    try:
        glist_info = await bot.get_group_list()
        await repalce_age(bot, glist_info)
        msg = '所有群友年龄信息手动更新完成'
        sv.logger.info(msg)
    except Exception as e:
        msg ='所有群友年龄信息手动更新失败：' + str(e)
        sv.logger.error(msg)
    await bot.send(ev, msg)

# 自动删除退群的群员信息
@sv.on_notice('group_decrease.leave')
async def leave_notice(session: NoticeSession):
    uid = str(session.ctx['user_id'])
    gid = int(session.ctx['group_id'])
    await del_mem(current_dir, gid, uid)
    hoshino.logger.info(f'{uid}已退出群{gid}，因此群员生日配置里已删除其信息')