import os
import asyncio
import hoshino
from hoshino import Service, priv
from .create_config import *
from .comp_birth import *
from .update_age import *


sv = Service('member_birthday', enable_on_default=True)

# 正常来说只要初始化一次就够了
@sv.on_fullmatch('群员生日初始化')
async def init_birth(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    # 首次启动时，若没有`config.yml`则创建配置文件
    _current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    if not os.path.exists(_current_dir):
        _bot = hoshino.get_bot()
        msg = '所有群的群成员信息正在初始化中，请耐心等待...\n（初始化时间受群数量和人数影响，总共两三百人大概要3分钟或者更久）'
        await bot.send(ev, msg)
        await create_yml(_bot, _current_dir)
        msg = '初始化成功，您可前往本文件所在的目录查看 `config.yml` 内容是否有误\n数据结构非常简单，user_id是QQ号，yes_age是昨天的年龄，tod_age是今天的年龄'
        await bot.send(ev, msg)
    else:
        msg = '初始化失败，文件已存在不可再初始化！\n为防止误触，不提供群内删除文件的命令，若想重新初始化，请手动到本文件目录删除`config.yml`'
        await bot.send(ev, msg)

# 推送生日祝福
@sv.scheduled_job('cron', hour='8', minute='00') # 早上8点推送祝福，让你在赶着上班上学的同时得到一丝温馨感（
async def auto_compare():
    bot = hoshino.get_bot()
    glist_info = await sv.get_enable_groups()
    for each_g in glist_info:
        gid = each_g['group_id']
        bir_list = judge_bir(gid)
        if bir_list:
            sv.logger.info(f'检测到今天群号{gid}里有{len(bir_list)}个B生日！')
            msg = get_bir_info(bir_list)
            await bot.send_group_msg(group_id=gid, message=msg)
        else:
            sv.logger.info(f'今天群号{gid}里没有群友生日欸~')

# 更新每天的年龄，运行起来也要挺久的时间
@sv.scheduled_job('cron', hour='2', minute='00') # 凌晨两点更新数据
async def auto_update():
    bot = hoshino.get_bot()
    superid = hoshino.config.SUPERUSERS[0]
    sv.logger.info('正在更新群友信息...预计用时几分钟')
    glist_info = await bot.get_group_list()
    for each_g in glist_info:
        gid = each_g['group_id']
        await repalce_age(bot, gid)
    sv.logger.info('所有群友年龄信息更新完成')
    msg = '所有群友年龄信息自动更新完成'
    await bot.send_private_msg(user_id=superid, message=msg)

# 测试用的
@sv.on_fullmatch('手动更新生日')
async def update_bir(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    superid = hoshino.config.SUPERUSERS[0]
    msg = '正在手动更新数据中...'
    await bot.send(ev, msg)
    sv.logger.info('正在更新群友信息...预计用时几分钟')
    glist_info = await bot.get_group_list()
    for each_g in glist_info:
        gid = each_g['group_id']
        await repalce_age(bot, gid)
    sv.logger.info('所有群友年龄信息更新完成')
    msg = '所有群友年龄信息手动更新完成'
    await bot.send_private_msg(user_id=superid, message=msg)
