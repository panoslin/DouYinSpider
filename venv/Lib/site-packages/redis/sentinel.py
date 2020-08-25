import os
import random
import weakref

from redis.client import StrictRedis
from redis.connection import ConnectionPool, Connection
from redis.exceptions import (ConnectionError, ResponseError, ReadOnlyError,
                              TimeoutError)
from redis._compat import iteritems, nativestr, xrange


class MainNotFoundError(ConnectionError):
    pass


class SubordinateNotFoundError(ConnectionError):
    pass


class SentinelManagedConnection(Connection):
    def __init__(self, **kwargs):
        self.connection_pool = kwargs.pop('connection_pool')
        super(SentinelManagedConnection, self).__init__(**kwargs)

    def __repr__(self):
        pool = self.connection_pool
        s = '%s<service=%s%%s>' % (type(self).__name__, pool.service_name)
        if self.host:
            host_info = ',host=%s,port=%s' % (self.host, self.port)
            s = s % host_info
        return s

    def connect_to(self, address):
        self.host, self.port = address
        super(SentinelManagedConnection, self).connect()
        if self.connection_pool.check_connection:
            self.send_command('PING')
            if nativestr(self.read_response()) != 'PONG':
                raise ConnectionError('PING failed')

    def connect(self):
        if self._sock:
            return  # already connected
        if self.connection_pool.is_main:
            self.connect_to(self.connection_pool.get_main_address())
        else:
            for subordinate in self.connection_pool.rotate_subordinates():
                try:
                    return self.connect_to(subordinate)
                except ConnectionError:
                    continue
            raise SubordinateNotFoundError  # Never be here

    def read_response(self):
        try:
            return super(SentinelManagedConnection, self).read_response()
        except ReadOnlyError:
            if self.connection_pool.is_main:
                # When talking to a main, a ReadOnlyError when likely
                # indicates that the previous main that we're still connected
                # to has been demoted to a subordinate and there's a new main.
                # calling disconnect will force the connection to re-query
                # sentinel during the next connect() attempt.
                self.disconnect()
                raise ConnectionError('The previous main is now a subordinate')
            raise


class SentinelConnectionPool(ConnectionPool):
    """
    Sentinel backed connection pool.

    If ``check_connection`` flag is set to True, SentinelManagedConnection
    sends a PING command right after establishing the connection.
    """

    def __init__(self, service_name, sentinel_manager, **kwargs):
        kwargs['connection_class'] = kwargs.get(
            'connection_class', SentinelManagedConnection)
        self.is_main = kwargs.pop('is_main', True)
        self.check_connection = kwargs.pop('check_connection', False)
        super(SentinelConnectionPool, self).__init__(**kwargs)
        self.connection_kwargs['connection_pool'] = weakref.proxy(self)
        self.service_name = service_name
        self.sentinel_manager = sentinel_manager

    def __repr__(self):
        return "%s<service=%s(%s)" % (
            type(self).__name__,
            self.service_name,
            self.is_main and 'main' or 'subordinate',
        )

    def reset(self):
        super(SentinelConnectionPool, self).reset()
        self.main_address = None
        self.subordinate_rr_counter = None

    def get_main_address(self):
        main_address = self.sentinel_manager.discover_main(
            self.service_name)
        if self.is_main:
            if self.main_address is None:
                self.main_address = main_address
            elif main_address != self.main_address:
                # Main address changed, disconnect all clients in this pool
                self.disconnect()
        return main_address

    def rotate_subordinates(self):
        "Round-robin subordinate balancer"
        subordinates = self.sentinel_manager.discover_subordinates(self.service_name)
        if subordinates:
            if self.subordinate_rr_counter is None:
                self.subordinate_rr_counter = random.randint(0, len(subordinates) - 1)
            for _ in xrange(len(subordinates)):
                self.subordinate_rr_counter = (
                    self.subordinate_rr_counter + 1) % len(subordinates)
                subordinate = subordinates[self.subordinate_rr_counter]
                yield subordinate
        # Fallback to the main connection
        try:
            yield self.get_main_address()
        except MainNotFoundError:
            pass
        raise SubordinateNotFoundError('No subordinate found for %r' % (self.service_name))

    def _checkpid(self):
        if self.pid != os.getpid():
            self.disconnect()
            self.reset()
            self.__init__(self.service_name, self.sentinel_manager,
                          is_main=self.is_main,
                          check_connection=self.check_connection,
                          connection_class=self.connection_class,
                          max_connections=self.max_connections,
                          **self.connection_kwargs)


class Sentinel(object):
    """
    Redis Sentinel cluster client

    >>> from redis.sentinel import Sentinel
    >>> sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
    >>> main = sentinel.main_for('mymain', socket_timeout=0.1)
    >>> main.set('foo', 'bar')
    >>> subordinate = sentinel.subordinate_for('mymain', socket_timeout=0.1)
    >>> subordinate.get('foo')
    'bar'

    ``sentinels`` is a list of sentinel nodes. Each node is represented by
    a pair (hostname, port).

    ``min_other_sentinels`` defined a minimum number of peers for a sentinel.
    When querying a sentinel, if it doesn't meet this threshold, responses
    from that sentinel won't be considered valid.

    ``sentinel_kwargs`` is a dictionary of connection arguments used when
    connecting to sentinel instances. Any argument that can be passed to
    a normal Redis connection can be specified here. If ``sentinel_kwargs`` is
    not specified, any socket_timeout and socket_keepalive options specified
    in ``connection_kwargs`` will be used.

    ``connection_kwargs`` are keyword arguments that will be used when
    establishing a connection to a Redis server.
    """

    def __init__(self, sentinels, min_other_sentinels=0, sentinel_kwargs=None,
                 **connection_kwargs):
        # if sentinel_kwargs isn't defined, use the socket_* options from
        # connection_kwargs
        if sentinel_kwargs is None:
            sentinel_kwargs = dict([(k, v)
                                    for k, v in iteritems(connection_kwargs)
                                    if k.startswith('socket_')
                                    ])
        self.sentinel_kwargs = sentinel_kwargs

        self.sentinels = [StrictRedis(hostname, port, **self.sentinel_kwargs)
                          for hostname, port in sentinels]
        self.min_other_sentinels = min_other_sentinels
        self.connection_kwargs = connection_kwargs

    def __repr__(self):
        sentinel_addresses = []
        for sentinel in self.sentinels:
            sentinel_addresses.append('%s:%s' % (
                sentinel.connection_pool.connection_kwargs['host'],
                sentinel.connection_pool.connection_kwargs['port'],
            ))
        return '%s<sentinels=[%s]>' % (
            type(self).__name__,
            ','.join(sentinel_addresses))

    def check_main_state(self, state, service_name):
        if not state['is_main'] or state['is_sdown'] or state['is_odown']:
            return False
        # Check if our sentinel doesn't see other nodes
        if state['num-other-sentinels'] < self.min_other_sentinels:
            return False
        return True

    def discover_main(self, service_name):
        """
        Asks sentinel servers for the Redis main's address corresponding
        to the service labeled ``service_name``.

        Returns a pair (address, port) or raises MainNotFoundError if no
        main is found.
        """
        for sentinel_no, sentinel in enumerate(self.sentinels):
            try:
                mains = sentinel.sentinel_mains()
            except (ConnectionError, TimeoutError):
                continue
            state = mains.get(service_name)
            if state and self.check_main_state(state, service_name):
                # Put this sentinel at the top of the list
                self.sentinels[0], self.sentinels[sentinel_no] = (
                    sentinel, self.sentinels[0])
                return state['ip'], state['port']
        raise MainNotFoundError("No main found for %r" % (service_name,))

    def filter_subordinates(self, subordinates):
        "Remove subordinates that are in an ODOWN or SDOWN state"
        subordinates_alive = []
        for subordinate in subordinates:
            if subordinate['is_odown'] or subordinate['is_sdown']:
                continue
            subordinates_alive.append((subordinate['ip'], subordinate['port']))
        return subordinates_alive

    def discover_subordinates(self, service_name):
        "Returns a list of alive subordinates for service ``service_name``"
        for sentinel in self.sentinels:
            try:
                subordinates = sentinel.sentinel_subordinates(service_name)
            except (ConnectionError, ResponseError, TimeoutError):
                continue
            subordinates = self.filter_subordinates(subordinates)
            if subordinates:
                return subordinates
        return []

    def main_for(self, service_name, redis_class=StrictRedis,
                   connection_pool_class=SentinelConnectionPool, **kwargs):
        """
        Returns a redis client instance for the ``service_name`` main.

        A SentinelConnectionPool class is used to retrive the main's
        address before establishing a new connection.

        NOTE: If the main's address has changed, any cached connections to
        the old main are closed.

        By default clients will be a redis.StrictRedis instance. Specify a
        different class to the ``redis_class`` argument if you desire
        something different.

        The ``connection_pool_class`` specifies the connection pool to use.
        The SentinelConnectionPool will be used by default.

        All other keyword arguments are merged with any connection_kwargs
        passed to this class and passed to the connection pool as keyword
        arguments to be used to initialize Redis connections.
        """
        kwargs['is_main'] = True
        connection_kwargs = dict(self.connection_kwargs)
        connection_kwargs.update(kwargs)
        return redis_class(connection_pool=connection_pool_class(
            service_name, self, **connection_kwargs))

    def subordinate_for(self, service_name, redis_class=StrictRedis,
                  connection_pool_class=SentinelConnectionPool, **kwargs):
        """
        Returns redis client instance for the ``service_name`` subordinate(s).

        A SentinelConnectionPool class is used to retrive the subordinate's
        address before establishing a new connection.

        By default clients will be a redis.StrictRedis instance. Specify a
        different class to the ``redis_class`` argument if you desire
        something different.

        The ``connection_pool_class`` specifies the connection pool to use.
        The SentinelConnectionPool will be used by default.

        All other keyword arguments are merged with any connection_kwargs
        passed to this class and passed to the connection pool as keyword
        arguments to be used to initialize Redis connections.
        """
        kwargs['is_main'] = False
        connection_kwargs = dict(self.connection_kwargs)
        connection_kwargs.update(kwargs)
        return redis_class(connection_pool=connection_pool_class(
            service_name, self, **connection_kwargs))
