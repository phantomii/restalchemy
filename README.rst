REST Alchemy
============

The Python REST HTTP Toolkit and Object Relational Mapper.


Migration commands
------------------

Create migrations:

::

  $ ra-new-migration --path examples/migrations/ --message "1st migration"
  $ ra-new-migration --path examples/migrations/ --message "2st migration" --depend 1st
  $ ra-new-migration --path examples/migrations/ --message "3st migration" --depend 2st
  $ ra-new-migration --path examples/migrations/ --message "4st migration"
  $ ra-new-migration --path examples/migrations/ --message "5st migration" --depend 3st --depend 4st


Apply migrations:

::

  $ ra-apply-migration --path examples/migrations/ --db-connection mysql://test:test@localhost/test -m 5st

> upgrade 1st
> upgrade 2st
> upgrade 3st
> upgrade 4st
> upgrade 5st


Rolled back migrations:

::

  $ ra-rollback-migration --path examples/migrations/ --db-connection mysql://test:test@localhost/test -m 4st
  
> downgrade 5st
> downgrade 4st

::

  $ ra-rollback-migration --path examples/migrations/ --db-connection mysql://test:OyO83AdIn9hbK3uz@cameron.synapse.net.ru/test -m 1st

> downgrade 3st
> downgrade 2st
> downgrade 1st
