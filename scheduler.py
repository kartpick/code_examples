import threading
import schedule
import logging
from class_CRUD import CRUD
from flask import flash
import time, Queue, datetime
from class_sharing import Sharing
from class_trace import Trace
from class_link import Link

global jobqueue, linkqueue

jobqueue        = Queue.Queue()
reminderqueue   = Queue.Queue()
linkqueue       = Queue.Queue()


class Scheduler:
"""
    Scheduler: class provides interface to initialize threads
    with different meaning, working separately.
"""      

    @classmethod
    def register_cron(self,task):
        """
            register_cron: gets Task-class object, reads formula
            and registers it in Queue. Callback checks in thread.
        """
        try:
            job = schedule.every(task.interval)
            job.unit = task.unit

            if task.unit in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
                job.start_day = job.unit
                job.unit = "weeks"
                job.at(task.at_time)
            elif task.unit in ('days', 'hours'):
                job.at(task.at_time)   

            global jobqueue

            job.do(jobqueue.put, task)
        except AssertionError:
            flash("Invalid schedule")

    @classmethod
    def register_link(cls, link):
        """
            register_link: gets Task-class object of file-chain, which
            has a lifetime, reads formula and registers it in Queue.
            Callback checks in thread.
        """
        try:
            global linkqueue
            interval = link.del_date - datetime.datetime.now()

            logging.info("New link register in scheduler with interval: %s" % interval)

            schedule.every(interval.seconds).seconds.do(cls.excecute_link, link)
        except AssertionError:
            flash("Invalid link registering")

    @classmethod
    def excecute_task(cls, task, queue):
        """
            excecute_task: removes scheduler task and makes 
            execution task for thread
        """
        queue.put(task)
        return schedule.CancelJob
        
        
    @classmethod
    def start(self):
        """
            start: activates listening threads, checks 
            data actuality and executes trash.
        """

        logging.info("Starting scheduler...") 
        for task in schedule.taskBank.get_all():
            if task.isActual():
                task._status = "Scheduled"
                task.save()            
                self.register(task)
            else:
                task.delete()

            for link in Link.get_all():
                self.register_link(link)

        logging.info("Scheduler started. Data checked.") 
        logging.info("Scheduler starts threads.") 

        try:
            link_worker_thread = ScheduleThread()
            link_worker_thread.start()
        
            """ Another thread loading """
        except:
            flash("Error while loading threads.")



           
    

class ScheduleThread(threading.Thread):
    """
        ScheduleThread: Simple thread. Example for developers.
    """
    @classmethod
    def run(cls):
        while True:
            schedule.run_pending()
            time.sleep(10)
            Scheduler.excecute_task()



class ScheduleWorkerThread(threading.Thread):
    @classmethod
    def run(cls):
        import logging
        while True:
            try:
                global jobqueue
                job_func = jobqueue.get(True, 60)
                logging.info("New task: %s"%job_func.destination)
                job_func()
                jobqueue.task_done()
                time.sleep(10)
            except Queue.Empty:
                continue
            except Exception as e:
                logging.info("worker traceback: " + Trace.exception_trace())
                logging.info("worker: %s" % str(e))



class ScheduleLinkWorkerThread(threading.Thread):
    @classmethod
    def run(cls):
        import logging
        while True:
            try:
                global linkqueue
                link = linkqueue.get(True, 60)
                logging.info("New link deletion task: %s" % link.guid)
                link.delete(link.guid)

                linkqueue.task_done()
                logging.info("Link deleted: %s" % link.guid)

                time.sleep(10)
            except Queue.Empty:
                continue
            except Exception as e:
                logging.info("Link thread worker traceback: " + Trace.exception_trace())
                logging.info("Worker: %s" % str(e))