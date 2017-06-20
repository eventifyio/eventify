"""
Eventify Event Store Models
"""
from sqlalchemy import Column, Integer, MetaData, Table, func
from sqlalchemy.dialects.postgresql import JSON, TIMESTAMP


def get_table(table_name, engine):
    """
    Get generic table object
    for use
    :param table_name:
    :param engine:
    """

    metadata = MetaData()

    table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, nullable=False, autoincrement=True),
        Column('event', JSON, nullable=False),
        Column('issued_at', TIMESTAMP, nullable=False, default=func.now())
    )
    metadata.create_all(engine)

    return table
