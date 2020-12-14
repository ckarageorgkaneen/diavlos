import logging
import functools

from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class MetadataError(Exception):
    pass


def _error(message):
    logger.error(message)
    raise MetadataError(message)


def handle_db_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PyMongoError as e:
            _error(str(e))
    return wrapper


def _query(uuid, type_=None):
    query = {'uuid': uuid}
    if type_ is not None:
        query['type'] = type_
    return query


class Metadata:
    _DB = 'services_database'
    _TABLE = 'metadata'
    _KEY = _TABLE

    def __init__(self, db_name=None, table_name=None):
        self._db_name = db_name or self._DB
        self._table_name = table_name or self._TABLE
        self.__db = None

    @property
    def _db(self):
        if self.__db is None:
            self.__db = MongoClient()[self._db_name][self._table_name]
        return self.__db

    @handle_db_error
    def _create(self, document):
        return self._db.insert_one(document)

    @handle_db_error
    def _read(self, query):
        return self._db.find_one(query)

    @handle_db_error
    def _update(self, query, fields, unset=False):
        operator = '$unset' if unset else '$set'
        if unset:
            fields = {
                f'{self._KEY}.{name}': ''
                for name in fields[self._KEY]
            }
        else:
            fields = fields
        return self._db.update_one(
            query, {operator: fields})

    @handle_db_error
    def _delete(self, query):
        return self._db.delete_one(query)

    def create(self, uuid, type_, **metadata):
        read_result = self.read(uuid, type_)
        if read_result is None:
            document = _query(uuid, type_)
            document[self._KEY] = metadata
            self._create(document)
            result = True
        else:
            result = False
        return result

    def read(self, uuid, type_):
        query = _query(uuid, type_)
        result = self._read(query)
        if result is not None:
            del result['_id']
        return result

    def update(self, uuid, type_, unset=False, **metadata):
        query = _query(uuid, type_)
        result = self._update(query, dict(metadata=metadata), unset=unset)
        return result.modified_count > 0

    def delete(self, uuid, type_):
        query = _query(uuid, type_)
        result = self._delete(query)
        return result.deleted_count > 0
