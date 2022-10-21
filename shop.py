import asyncio
import json
import logging
import os
import random
import re
import time
import uuid
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Optional, List

import databases
import discord
import pytz
from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from discord import app_commands, MessageType, Member
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine

from consts import CONSTS
from models import giveaways, metadata, user_score, user_info, score_exchange
from settings import SETTINGS

# 本体设置，服务器ID
MY_GUILD = discord.Object(id=SETTINGS.GUILD)

# 数据库设置
database = databases.Database(SETTINGS.DATABASE)
engine = create_async_engine(
    SETTINGS.DATABASE, echo=True
)

# 定时器
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///scheduler.db')
}
executors = {
    # 'default': ThreadPoolExecutor(20),
    # 'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 100
}

# 记录老板和消息响应
user_roll_map = {}
to_delete_roll_id = []

# 当不存在的时候，创建images和logs文件夹
if not os.path.exists('images'):
    os.mkdir('images')
if not os.path.exists('logs'):
    os.mkdir('logs')


async def save_card_info(image_name, image_content):
    """保存图片"""
    with open(image_name, 'wb') as f:
        f.write(image_content)
        logger.info(f'save image {image_name} success')


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.scheduler = None
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def on_ready(self):
        """初始化的一些操作"""
        # 初始化定时器
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores, executors=executors, job_defaults=job_defaults,
            timezone=pytz.timezone(SETTINGS.TIMEZONE),
            # event_loop=asyncio.new_event_loop()
        )
        logger.info('Logged on as', self.user)

    async def on_message(self, message: discord.Message):
        """接收消息的函数"""
        logger.debug(f'message: {message}')
        # don't respond to ourselves
        if message.author == self.user:
            return


intents = discord.Intents.default()
intents.dm_messages = True
intents.message_content = True
client = MyClient(intents=intents)


async def get_user_info(user_id):
    """从数据库中获取指定id的用户信息,返回dict类型"""
    user_id = str(user_id)
    query = user_info.select().where(user_info.c.id == user_id)
    result = await database.fetch_one(query)
    if result:
        return dict(result)
    return {}


@client.tree.command()
@app_commands.describe(
    member='看指定成员的积分，不输入则默认为当前发出指令的成员'
)
async def rank(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """显示member的积分"""
    member = member or interaction.user
    # 获取成员id的积分
    user_id = member.id
    result = await get_user_info(user_id)
    if result:
        score = result['total_score']
    else:
        score = 0
        logger.warning(f'{member} {user_id} 当前没有积分')
    await interaction.response.send_message(f'{member} 当前积分为 {score}')


async def add_user_score(user_id: int, score: float, score_type: str = ''):
    """给某个用户增加积分的数据库操作
    :param user_id: 用户的id
    :param score: 增加的积分
    :param score_type: 积分的类型，默认为空，预留扩展"""
    query = user_info.select().where(user_id == user_info.c.id)
    result = await database.fetch_one(query)
    if result:
        # 如果有记录，则更新
        query = user_info.update().where(user_id == user_info.c.id).values(total_score=score + result['total_score'])
        result = await database.execute(query)
        logger.info(f'update user {user_id} score: {score}')
    else:
        # 如果没有记录，则插入
        query = user_info.insert().values(id=user_id, total_score=score)
        result = await database.execute(query)
        logger.info(f'insert user {user_id} score: {score} result: {result}')
    # 记录积分变动
    query = user_score.insert().values(user_id=user_id, score=score, score_type=score_type)
    result = await database.execute(query)
    logger.info(f'insert user {user_id} score type: {score} result: {result}')


def get_score_exchange_details(exchange_id):
    """获取积分兑换详情"""
    query = score_exchange.select().where(score_exchange.c.id == exchange_id)
    result = database.fetch_one(query)
    return result


def get_all_score_exchange():
    """获取所有积分兑换详情"""
    query = score_exchange.select()
    result = database.fetch_all(query)
    return result


@client.tree.command()
@app_commands.describe(
    details='积分兑换内容',
    score='所需兑换积分'
)
async def add_exchange(interaction: discord.Interaction, details: str, score: int):
    """
    添加积分兑换内容
    :param interaction:
    :param details: 兑换内容
    :param score: 所需积分
    :return:
    """
    # 获取用户
    user = interaction.user
    # 新增积分兑换项
    query = score_exchange.insert().values(
        details=details,
        score=score,
    )
    result = await database.execute(query)
    logger.info(f'{user.display_name} 新增兑换内容 {details}，所需积分为 {score}')
    await interaction.response.send_message(f'新增 {details}，所需积分为 {score}')


@client.tree.command()
@app_commands.describe(
    exchange_id='积分id',
)
async def delete_exchange(interaction: discord.Interaction, exchange_id: int):
    """
    删除积分兑换内容
    :param interaction:
    :param exchange_id: 积分id
    :return:
    """
    # 获取用户
    user = interaction.user
    # 查询该项内容
    exist_result = await get_score_exchange_details(exchange_id)
    # 提取积分兑换内容
    details, score = exist_result['details'], exist_result['score']
    query = score_exchange.delete().where(
        score_exchange.c.id == exchange_id,
    )
    delete_result = await database.execute(query)

    logger.info(f'{user.display_name} 删除 {exchange_id} 兑换: {details}')
    await interaction.response.send_message(f'删除兑换ID {exchange_id}: {details}')


@client.tree.command()
@app_commands.describe(
    exchange_id='积分id',
    update_details='兑换详细内容',
)
async def update_exchange(interaction: discord.Interaction, exchange_id: int, update_details: str):
    """
    更新积分兑换内容
    :param interaction:
    :param exchange_id: 积分id
    :param details: 兑换详细内容
    :return:
    """
    # 获取用户
    user = interaction.user
    # 查询该项内容
    exist_result = await get_score_exchange_details(exchange_id)
    # 提取积分兑换内容
    details, score = exist_result['details'], exist_result['score']
    query = score_exchange.update().where(
        score_exchange.c.id == exchange_id,
    ).values(
        details=update_details
    )
    update_result = await database.execute(query)
    logger.info(f'{user.display_name} 更新 {exchange_id} 兑换: {details}: {update_result}')
    await interaction.response.send_message(f'更新兑换ID {exchange_id}: {details}')


@client.tree.command()
async def shop(interaction: discord.Interaction):
    """查看积分兑换表"""
    # 从数据库中查看积分兑换表
    result = await get_all_score_exchange()
    # 发送频道的信息
    result_str = "积分兑换列表:\n"
    # 输出一个表格形式的文字，显示积分兑换表的详情
    for item in result:
        # 使用rjust右对齐，积分在最后
        details_item = f"{item['id']}. {item['details']}".ljust(30, '-')
        result_str += f'{details_item} {item["score"]}\n'
    await interaction.response.send_message(result_str)


@client.tree.command()
@app_commands.describe(
    exchange_id='积分id',
)
async def ex(interaction: discord.Interaction, exchange_id: int):
    """用户发送兑换消息，扣除user_info的积分进行兑换"""
    user = interaction.user

    # 查询该条积分的记录
    exchange_result = await get_score_exchange_details(exchange_id)
    # 查看用户的积分余额是否足够扣除积分
    exchange_detail = exchange_result['details']
    score = exchange_result['score']
    current_user_info = await get_user_info(user_id=user.id)
    # fixme 需要加临时锁防止兑换
    user_now_score = current_user_info['total_score']
    if user_now_score < score:
        # 不能兑换并发送消息
        await interaction.response.send_message(f'抱歉，你的积分不够兑换: {exchange_detail}')
    else:
        query = user_info.update().where(
            user_info.c.id == user.id,
        ).values(
            total_score=user_now_score - score
        )
        update_result = await database.execute(query)
        logger.info(f'{user.display_name} exchange {exchange_detail} score {score} success')
        await interaction.response.send_message(f'兑换 {exchange_detail} 成功')


async def async_main():
    # logging日志的初始化
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        filename='logs/discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    discord_logger.addHandler(handler)

    async with engine.begin() as conn:
        # await conn.run_sync(metadata.drop_all)  # debug
        await conn.run_sync(metadata.create_all)

    await database.connect()
    # await engine.dispose()

    logger.info('start scheduler')


asyncio.run(async_main())
logger.info(f'start app')

client.run(SETTINGS.TOKEN)
logger.info(f'stopped app')
