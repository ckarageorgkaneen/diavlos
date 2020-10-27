import logging
import functools

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getlogger(__name__)


class MetadataError(Exception):
    pass


def _error(message):
    logger.error(message)
    raise MetadataError(message)


def handle_db_timeout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServerSelectionTimeoutError as e:
            _error(str(e))
    return wrapper


def _query(uuid, type_=None):
    query = {'uuid': uuid}
    if type_ is not None:
        query['type'] = type_
    return query


class Metadata(object):
    def __init__(self, db_name):
        self._db_name = db_name
        self.__db = None

    @property
    def _db(self):
        if self.__db is None:
            self.__db = MongoClient()[self._db_name].metadata
        return self.__db

    @handle_db_timeout
    def _db_create(self, document):
        return self._db.insert_one(document)

    @handle_db_timeout
    def _db_read(self, query):
        return self._db.find_one(query)

    @handle_db_timeout
    def _db_update(self, query, replacement, force=False):
        set_operator = '$set' if force else '$setOnInsert'
        return self._db.update_one(
            query, {set_operator: replacement}, upsert=True)

    @handle_db_timeout
    def _db_delete(self, query):
        return self._db.delete_one(query)

    def create(self, uuid, type_, metadata):
        read_successful, read_metadata = self.read(uuid, type_)
        if read_successful:
            result = False, read_metadata
        else:
            document = _query(uuid, type_)
            document['metadata'] = metadata
            added_metadata = self._db_create(document)
            del added_metadata['id_']
            result = True, added_metadata
        return result

    def read(self, uuid, type_):
        find_result = self._db_read(_query(uuid, type_))
        if find_result is None:
            success = False
        else:
            success = True
            del find_result['_id']
        result = success, find_result
        return result

    def update(self, uuid, type_, metadata, force=False):
        query = _query(uuid, type_)
        replacement = dict(query, metadata=metadata)
        update_result = self._db_update(query, replacement, force=force)
        if force:
            success = update_result.modified_count > 0
        else:
            success = True
        result = success, replacement
        return result

    def delete(self, uuid, type_):
        read_successful, read_metadata = self.read(uuid, type_)
        if read_successful:
            delete_result = self._db_delete(_query(uuid, type_))
            success = delete_result.n > 0
        else:
            success = False
        result = success, read_metadata
        return result
