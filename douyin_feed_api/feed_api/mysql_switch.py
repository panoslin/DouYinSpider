#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/13/18
# IDE: PyCharm

from mysql.connector.errors import OperationalError, ProgrammingError, DatabaseError
import mysql.connector
from functools import wraps
import configparser


class MysqlSwitch:
    def __init__(self, configuration="sample_config.ini"):
        """
        This is a decorator and it works like a switch for mysql connection:
        connect to the database before the operations(i.e. whatever the operations in the decorated func)
        and commit/close the connection after the operation

        self.simulate : if True, the database operation will not be commit or else the opposite. Defaule True

        :param configuration: a config file configparser.ConfigParser() or a path to the config file.
        It should contain the host, port, usrname, psw and database to connect to the corresponding database.
        In this example, two database are concerned.
        """
        if isinstance(configuration, configparser.ConfigParser):
            self.config = configuration
        elif isinstance(configuration, str):
            PathConfig = configuration
            self.config = configparser.ConfigParser()
            self.config.read(PathConfig)

        self.simulate = eval(self.config.get('miscellaneous', 'simulate'))


    def __call__(self, func):
        @wraps(func)
        def wrapup(*args, **kwargs):
            res = None
            kwargs['conn'], kwargs['conn_local'], kwargs['cur'], kwargs['cur_local'] = self.connect()
            try:
                res = func(*args, **kwargs)
            except (OperationalError, ProgrammingError, DatabaseError) as e:
                self.rollback(kwargs['conn'], kwargs['conn_local'])
                self.close(kwargs['conn'], kwargs['conn_local'], kwargs['cur'], kwargs['cur_local'])
                raise e
            except Exception as e:
                self.rollback(kwargs['conn'], kwargs['conn_local'])
                self.close(kwargs['conn'], kwargs['conn_local'], kwargs['cur'], kwargs['cur_local'])
                raise e
            finally:
                self.commit(kwargs['conn'], kwargs['conn_local'],simulate=self.simulate)
                self.close(kwargs['conn'], kwargs['conn_local'], kwargs['cur'], kwargs['cur_local'])
                return res
        return wrapup

    def connect(self):
        # Construct MySQL connect
        # online DB config
        database = self.config.get('mysql', 'database')
        user_name = self.config.get('mysql', 'user_name')
        password = self.config.get('mysql', 'password')
        host = self.config.get('mysql', 'host')
        port = self.config.getint('mysql', 'port')

        # local DB config
        database_local = self.config.get('mysql', 'database_local')
        user_name_local = self.config.get('mysql', 'user_name_local')
        password_local = self.config.get('mysql', 'password_local')
        host_local = self.config.get('mysql', 'host_local')
        port_local = self.config.getint('mysql', 'port_local')

        conn = mysql.connector.connect(user=user_name, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        conn_local = mysql.connector.connect(user=user_name_local, password=password_local, host=host_local,
                                             port=port_local, database=database_local)
        cur_local = conn_local.cursor()
        return conn, conn_local, cur, cur_local

    @ staticmethod
    def close(conn, conn_local, cur, cur_local):
        cur.close()
        conn.close()
        cur_local.close()
        conn_local.close()

    @staticmethod
    def commit(conn, conn_local, simulate=True):
        if simulate is False:
            conn.commit()
            conn_local.commit()
        else:
            pass

    @staticmethod
    def rollback(conn, conn_local):
        conn.rollback()
        conn_local.rollback()
