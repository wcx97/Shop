import sqlalchemy

metadata = sqlalchemy.MetaData()

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

