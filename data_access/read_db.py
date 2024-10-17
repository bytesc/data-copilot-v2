import pandas as pd
from sqlalchemy import text, inspect

from data_access.db_conn import engine

tables_data = None


def get_foreign_keys():
    inspector = inspect(engine)
    foreign_keys = {}
    for table_name in inspector.get_table_names():
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            foreign_keys[table_name] = {}
            for fk in fks:
                for column in fk['constrained_columns']:
                    foreign_keys[table_name][column] = (
                        fk['referred_table'],
                        fk['referred_columns'][0]
                    )
    return foreign_keys


def get_table_and_column_comments():
    inspector = inspect(engine)
    table_comments = {}
    column_comments = {}
    table_names = inspector.get_table_names()
    for table_name in table_names:
        table_comment = inspector.get_table_comment(table_name)
        table_comments[table_name] = table_comment['text']
        columns = inspector.get_columns(table_name)
        column_comments[table_name] = {}
        for column in columns:
            column_comments[table_name][column['name']] = column['comment']
    return [table_comments, column_comments]


def get_data_from_db():
    global tables_data
    if tables_data is None:
        with engine.connect() as connection:
            query = text("SHOW TABLES")
            tables = connection.execute(query).fetchall()

            # 准备一个字典来存储所有表的DataFrame
            tables_data = {}

            # 遍历所有表名
            for table_name in tables:
                table_name = table_name[0]  # 表名是一个元组，取第一个元素
                query = text(f"SELECT * FROM {table_name}")  # 构造查询语句
                tables_data[table_name] = pd.read_sql(query, connection)  # 读取表内容到DataFrame

            connection.close()

    # 打印每个表的内容
    # for table_name, table_df in tables_data.items():
    #     print(f"Table: {table_name}")
    #     print(table_df)
    #     print("###########################################\n\n")

    # # 创建一个字典来存储合并后的DataFrame
    # merged_tables_data = {}
    #
    # # 遍历所有表，尝试将它们与其他表根据公共列连接
    # merged_table_names = set()  # 用于存储已合并的表名组合，避免重复
    # for table_name1, table_df1 in tables_data.items():
    #     for table_name2, table_df2 in tables_data.items():
    #         if table_name1 != table_name2 and (table_name2, table_name1) not in merged_table_names:
    #             # 检查两个表是否有公共列
    #             common_columns = set(table_df1.columns).intersection(set(table_df2.columns))
    #             if common_columns:
    #                 # 如果有公共列，则进行等值连接
    #                 merged_df = pd.merge(table_df1, table_df2, on=list(common_columns), how='outer')
    #                 # 创建新表名，并确保表名按字母顺序排序
    #                 sorted_table_names = sorted([table_name1, table_name2])
    #                 merged_table_name = "_".join(sorted_table_names)
    #                 # 将合并后的DataFrame添加到merged_tables_data
    #                 merged_tables_data[merged_table_name] = merged_df
    #                 # 添加已合并的表名组合到集合中，避免重复
    #                 merged_table_names.add((table_name1, table_name2))
    #                 # 标记表名1和表名2已被合并，不需要单独添加
    #                 merged_table_names.add(table_name1)
    #                 merged_table_names.add(table_name2)

    # # 添加没有被合并的原始表到结果字典
    # for table_name, table_df in tables_data.items():
    #     if table_name not in merged_table_names:
    #         merged_tables_data[table_name] = table_df

    # return tables_data, merged_tables_data
    keys = get_foreign_keys()
    comments = get_table_and_column_comments()
    return tables_data, keys, comments


if __name__ == "__main__":
    data = get_data_from_db()
    print(type(data), "\n")
    print(data[2][1])
    print("###########################################\n\n")
    # for table_name, table_df in mdata.items():
    #     print(f"Table: {table_name}")
    #     print(table_df)
    #     print(type(table_df))

