# Code examples

## Scheduler

This class is a CRON controller. Uses multiple custom threads, which listen global queues of tasks.
Scheduler provides interfaces to start threads, and register tasks in queues.

For low coupling, scheduler works with abstract threads. You can create lots of custom thread Workers, to handle
different tasks. 

## Link class

Class example. Derives simple methods to work with its database entity, and some special. This class doesn`t have interfaces for scheduler. If you want to use it in scheduler, you need to create LinkSchedulerTask class, which will use Decorator design pattern.
