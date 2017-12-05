"""
All database related infrastructure lives here
"""

import abc
import contextlib
import datetime
import json
import logging
import os
import threading

import sqlalchemy
from sqlalchemy import orm, event, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext import mutable

log = logging.getLogger(__name__)

def add_engine_pidguard(engine):
    """Add multiprocessing guards.

    Forces a connection to be reconnected if it is detected
    as having been shared to a sub-process.

    http://docs.sqlalchemy.org/en/rel_1_0/faq/connections.html
    #how-do-i-use-engines-connections-sessions-with-python-multiprocessing-or-os-fork
    """

    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        connection_record.info['pid'] = os.getpid()

    @event.listens_for(engine, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        if engine.dialect.name == 'sqlite':
            return
        pid = os.getpid()
        if connection_record.info['pid'] != pid:
            # substitute log.debug() or similar here as desired
            log.info(
                "Parent process %(orig)s forked (%(newproc)s) with an open "
                "database connection, "
                "which is being discarded and recreated." %
                {"newproc": pid, "orig": connection_record.info['pid']})
            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
            )
        # Following code prevents 'Mysql has gone away' errors
        try:
            try:
                dbapi_connection.ping(False)
            except TypeError:
                dbapi_connection.ping()
        except dbapi_connection.OperationalError as e:
            if e.args[0] in (2006, 2013, 2014, 2045, 2055):
                raise e.DisconnectionError()
            else:
                raise


class DBConfig(metaclass=abc.ABCMeta):
    """
    Usage:
        subclass this, overriding _config, POOL_SIZE and POOL_RECYCLE_SECONDS
        Note: `utf8mb4` is recommended for mysql, as starting with 5.6 mysql supports 4 bytes for utf8 with this charset type
    """
    _config = {
        'dialect': 'mysql',
        'driver': 'pymysql',
        'username': '',
        'password': '',
        'host': '',
        'port': '3306',
        'database': '',
        'charset': 'utf8mb4'
    }
    DB_URI = '{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}?charset={charset}'
    MYSQL_URI = '{dialect}+{driver}://{username}:{password}@{host}:{port}/?charset={charset}'

    POOL_SIZE = 10
    POOL_RECYCLE_SECONDS = 1000

    def get_database_name(self):
        return self._config['database']

    def get_uri(self, ignore_database=False):
        if ignore_database:
            return self.MYSQL_URI.format(**self._config)
        return self.DB_URI.format(**self._config)


class BaseModel(object):
    __abstract__ = True
    __table__ = None

    id = sqlalchemy.Column('id', sqlalchemy.Integer, autoincrement=True, primary_key=True)

    def __init__(self, **new_data):
        self.update(new_data)

    @classmethod
    def get_or_create_no__init__(model, session, **kwargs):
        # Check if record exists in database
        object = session.query(model).filter_by(**kwargs).first()
        if object is None:
            return model()
        return object

    @classmethod
    def get_or_create(model, session, **kwargs):
        """ Get the row from the model or create one.

        :param session: The SQL Alchemy session.
        :param kwargs: The arguments for the model.
        :return: The row you are interested in.
        """
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            return model(**kwargs)

    def update(self, allow_invalid_attr=True, **data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                if not allow_invalid_attr:
                    raise AttributeError
                continue

    def to_dict(self):
        """ Returns a flat dictionary from a model. """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class DBInterface(object):
    """
    THREAD and PROCESS safe interface to sqlalchemy engine

    """
    _instances = dict()
    _thread_lock = threading.RLock()

    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        self.db_url = db_config.get_uri()
        self.pool_size = db_config.POOL_SIZE
        self.pool_recycle = db_config.POOL_RECYCLE_SECONDS
        self.engine = None
        self.BASE_MODEL = None
        self.reinit_engine()
        self._new_session_factory = orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self._session_factory_with_autocommit = orm.sessionmaker(bind=self.engine, autocommit=True)
        self._scoped_session_factory = orm.scoped_session(self._new_session_factory)
        self._scoped_session_factory_with_auto_commit = orm.scoped_session(self._session_factory_with_autocommit)

    @classmethod
    def create_database(cls, db_config: DBConfig, delete_existing=False):
        """
        Create a database
        TODO: This method is WIP
        """
        db_name = db_config.get_database_name()
        engine = sqlalchemy.create_engine(db_config.get_uri(ignore_database=True), pool_size=1, pool_recycle=100)
        if delete_existing:
            prompt = input("Database would be deleted. Do you wish to continue?\n>")
            if prompt == "I agree":
                log.info('Deleting database if it exists....')
                engine.execute('DROP DATABASE IF EXISTS {}'.format(db_name))
            else:
                print("Try again next time. Your response: {} Expected response: I agree".format(prompt))
        log.info('Creating database....{}'.format(db_name))
        engine.execute('CREATE DATABASE IF NOT EXISTS {}'.format(db_name))
        log.info('Successfully created database with name {}'.format(db_name))

    def curate_database_encoding_to_utf8(self):
        """
        Sometimes sqlalchemy throws unicode related encoding issues because the collation on the database side is not correct
        http://stackoverflow.com/questions/2108824/mysql-incorrect-string-value-error-when-save-unicode-string-in-django
        """
        log.info('Curating database to converting coillation to utf8')
        self.engine.execute("ALTER DATABASE `{}` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'".format(
            self.db_config.get_database_name()))
        sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '{}'".format(
            self.db_config.get_database_name())
        records = self.engine.execute(sql)
        for record in records:
            sql = "ALTER TABLE `{}` convert to character set DEFAULT COLLATE DEFAULT".format(record[0])
            self.engine.execute(sql)

    @classmethod
    def singleton_instance(cls, db_config: DBConfig):
        if db_config.get_uri() not in cls._instances:
            with cls._thread_lock:
                if db_config.get_uri() not in cls._instances:
                    cls._instances[db_config.get_uri()] = cls(db_config=db_config)
        return cls._instances[db_config.get_uri()]

    @contextlib.contextmanager
    def tx_session(self, nested=True):
        """Context manager which provides transaction management for the nested
           block. A transaction is started when the block is entered, and then either
           committed if the block exits without incident, or rolled back if an error
           is raised.

           Nested (SAVEPOINT) transactions are enabled by default, unless nested=False is
           passed, meaning that this context manager can be nested within another and the
           transactions treated as independent units-of-work from the perspective of the nested
           blocks. If the error is handled further up the chain, the outer transactions will
           still be committed, while the inner ones will be rolled-back independently."""
        session = self.new_session()
        session.begin(nested=nested)
        try:
            yield session
        except Exception as e:
            # Roll back if the nested block raised an error
            session.rollback()
            log.error('Exception happened, rolling back {}'.format(e.__class__))
        else:
            # Commit if it didn't (so flow ran off the end of the try block)
            session.commit()
        finally:
            session.close()

    def reinit_engine(self, add_pidguard=True):
        log.info("Reinit database: {}".format(self.db_url))
        self.engine = sqlalchemy.create_engine(self.db_url, pool_size=self.pool_size, pool_recycle=self.pool_recycle)
        if add_pidguard:
            add_engine_pidguard(self.engine)
        if self.BASE_MODEL is None:
            # Models have probably been defined using the existing BASE_MODEL, do not create a new one
            self.BASE_MODEL = declarative_base(cls=BaseModel)
        self.BASE_MODEL.metadata.bind = self.engine

    def new_session(self, autocommit=False):
        if self.engine is None:
            raise RuntimeError('{}: Call to DBInterface().init_engine() is missing'.format(self.db_url))
        if autocommit:
            return self._session_factory_with_autocommit()
        return self._new_session_factory()

    def scoped_session(self, autocommit=False):
        if self.engine is None:
            raise RuntimeError('{}: Call to DBInterface().init_engine() is missing'.format(self.db_url))
        if autocommit:
            self._scoped_session_factory_with_auto_commit()
        return self._scoped_session_factory()

    def create_tables(self, delete_existing):
        log.info("Creating tables...")
        if self.engine is None:
            raise RuntimeError('{}: Call to DBInterface().init_engine() is missing'.format(self.db_url))
        if delete_existing:
            self.drop_tables()
        log.info('Creating tables..')
        self.BASE_MODEL.metadata.create_all(checkfirst=False)

    def drop_tables(self):
        if self.engine is None:
            raise RuntimeError('{}: Call to DBInterface().init_engine() is missing'.format(self.db_url))
        log.info('Dropping existing tables..')
        self.BASE_MODEL.metadata.drop_all()

    def bootstrap_db(self, delete_existing=True):
        """
        This method is supposed to be run manually, given the risks.
        :return:
        """
        prompt = input("All exisiting tables will be deleted. Do you wish to continue?\n>")
        if prompt == "I agree":
            log.info('Setting up database..')
            self.create_tables(delete_existing=delete_existing)
            log.info('Database setup completed')
        else:
            print("Try again next time. Your response: {} Expected response: I agree".format(prompt))


class JSONEncodedDict(TypeDecorator):
    impl = sqlalchemy.Text

    def serialize(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.__str__()
        return obj

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, default=self.serialize)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                value = json.loads(value)
            except ValueError:
                # nothing we can do if this happens.
                value = {}

        return value


mutable.MutableDict.associate_with(JSONEncodedDict)
