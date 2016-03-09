"""Concept example of `Dependency Injector`."""

import sqlite3

from dependency_injector import catalogs
from dependency_injector import providers
from dependency_injector import injections


class UsersService(object):
    """Users service, that has dependency on database."""

    def __init__(self, db):
        """Initializer."""
        self.db = db


class AuthService(object):
    """Auth service, that has dependencies on users service and database."""

    def __init__(self, db, users_service):
        """Initializer."""
        self.db = db
        self.users_service = users_service


class Services(catalogs.DeclarativeCatalog):
    """Catalog of service providers."""

    @providers.Singleton
    def database():
        """Provide database connection.

        :rtype: providers.Provider -> sqlite3.Connection
        """
        return sqlite3.connect(':memory:')

    @providers.Factory
    @injections.inject(db=database)
    def users(**kwargs):
        """Provide users service.

        :rtype: providers.Provider -> UsersService
        """
        return UsersService(**kwargs)

    @providers.Factory
    @injections.inject(db=database)
    @injections.inject(users_service=users)
    def auth(**kwargs):
        """Provide users service.

        :rtype: providers.Provider -> AuthService
        """
        return AuthService(**kwargs)


# Retrieving catalog providers:
users_service = Services.users()
auth_service = Services.auth()

# Making some asserts:
assert users_service.db is auth_service.db is Services.database()
assert isinstance(auth_service.users_service, UsersService)
assert users_service is not Services.users()
assert auth_service is not Services.auth()


# Making some "inline" injections:
@injections.inject(users_service=Services.users)
@injections.inject(auth_service=Services.auth)
@injections.inject(database=Services.database)
def example(users_service, auth_service, database):
    """Example callback."""
    assert users_service.db is auth_service.db
    assert auth_service.db is database
    assert database is Services.database()


# Making a call of decorated callback:
example()


# Overriding auth service provider and making some asserts:
class ExtendedAuthService(AuthService):
    """Extended version of auth service."""

    def __init__(self, db, users_service, ttl):
        """Initializer."""
        self.ttl = ttl
        super(ExtendedAuthService, self).__init__(db=db,
                                                  users_service=users_service)


class OverriddenServices(Services):
    """Catalog of service providers."""

    @providers.override(Services.auth)
    @providers.Factory
    @injections.inject(db=Services.database)
    @injections.inject(users_service=Services.users)
    @injections.inject(ttl=3600)
    def auth(**kwargs):
        """Provide users service.

        :rtype: providers.Provider -> AuthService
        """
        return ExtendedAuthService(**kwargs)


auth_service = Services.auth()

assert isinstance(auth_service, ExtendedAuthService)
