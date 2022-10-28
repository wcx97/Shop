import sqlalchemy

metadata = sqlalchemy.MetaData()

# 抽奖表
giveaways = sqlalchemy.Table(
    'giveaway',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('code', sqlalchemy.String),
    sqlalchemy.Column('start_time', sqlalchemy.DateTime),
    sqlalchemy.Column('end_time', sqlalchemy.DateTime),
    sqlalchemy.Column('minutes', sqlalchemy.Integer),
    sqlalchemy.Column('winners', sqlalchemy.Integer),
    sqlalchemy.Column('activate', sqlalchemy.Boolean, default=True),
)

# 定时恢复名字表
nick_temp = sqlalchemy.Table(
    'nick_temp',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('change_time', sqlalchemy.DateTime),
)

# 人员积分详情
user_score = sqlalchemy.Table(
    'user_score',
    metadata,
    # 递增id
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('user_id', sqlalchemy.String),
    # 获得积分
    sqlalchemy.Column('score', sqlalchemy.Integer, default=0),
    # 积分类型 目前为 text image
    sqlalchemy.Column('score_type', sqlalchemy.String),
    sqlalchemy.Column('create_time', sqlalchemy.DateTime, default=sqlalchemy.func.now()),
)

# 成员信息表，包括用户积分和生日
user_info = sqlalchemy.Table(
    'user_info',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    # 名片文件名，默认为 id.jpg
    sqlalchemy.Column('card', sqlalchemy.String, default=''),
    # 生日
    sqlalchemy.Column('birthday_month', sqlalchemy.Integer),
    sqlalchemy.Column('birthday_day', sqlalchemy.Integer),
    # 总积分
    sqlalchemy.Column('total_score', sqlalchemy.Float, default=0.0),
    sqlalchemy.Column('create_time', sqlalchemy.DateTime, default=sqlalchemy.func.now()),
    sqlalchemy.Column('update_time', sqlalchemy.DateTime, default=sqlalchemy.func.now(),
                      onupdate=sqlalchemy.func.now()),
)

# 积分兑换项表
score_exchange = sqlalchemy.Table(
    'score_exchange',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('details', sqlalchemy.String),
    sqlalchemy.Column('score', sqlalchemy.Float),
    sqlalchemy.Column('stock', sqlalchemy.Integer),
    sqlalchemy.Column('is_activate', sqlalchemy.Boolean, default=True),
    sqlalchemy.Column('create_time', sqlalchemy.DateTime, default=sqlalchemy.func.now()),
    sqlalchemy.Column('update_time', sqlalchemy.DateTime, default=sqlalchemy.func.now(),
                      onupdate=sqlalchemy.func.now())
)

# 积分兑换记录
score_exchange_record = sqlalchemy.Table(
    'score_exchange_record',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    # 兑换用户的id
    sqlalchemy.Column('user_id', sqlalchemy.String),
    # 兑换值为 score_exchange 的主键id
    sqlalchemy.Column('exchange_id', sqlalchemy.Integer),
    sqlalchemy.Column('score', sqlalchemy.Float),
    sqlalchemy.Column('create_time', sqlalchemy.DateTime, default=sqlalchemy.func.now())
)


# 彩蛋幸运成员记录
egg_lucky_record = sqlalchemy.Table(
    'egg_lucky_record',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    # 成员id
    sqlalchemy.Column('user_id', sqlalchemy.String),
    sqlalchemy.Column('user_name', sqlalchemy.String),
    sqlalchemy.Column('message_id', sqlalchemy.String),
    sqlalchemy.Column('message_channel_id', sqlalchemy.String),
    sqlalchemy.Column('message_channel_name', sqlalchemy.String),
    sqlalchemy.Column('message_guild_id', sqlalchemy.String),
    # 彩蛋内容
    sqlalchemy.Column('details', sqlalchemy.String),
    sqlalchemy.Column('create_time', sqlalchemy.DateTime, default=sqlalchemy.func.now()),
)
