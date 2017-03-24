from multiprocessing import Pool, Manager, Process, Lock, Queue, Value, Array, Pipe, TimeoutError
import multiprocessing as mp
import concurrent.futures
import time
import os
from timeit import default_timer as timer
import struct
import itertools as it
import math
import random as rnd
import time

def sendMsgsToMultiServer(webservice_pipe, handlerArgs):
    curProcPID = os.getpid()
    #webservice_pipe.send( struct.pack("<uQ", (curProcPID, seqID, str(curProcPID) + "_" + str(seqID)) ) )
    secs = rnd.randint(1, 20)
    time.sleep(secs)
    handlerID = handlerArgs[0]
    seqID = handlerArgs[1]
    #webservice_pipe.send( curProcPID, handlerID, seqID )
    webservice_pipe.send(curProcPID)
    webservice_pipe.send(handlerID)
    webservice_pipe.send(seqID)
    print("from Web-service: curProcPID = ", curProcPID)
    #webservice_pipe.send( seqID )
    webservice_pipe.close()
    return secs

def recvWebServiceMsg(multiServer_pipe):
    #print("multiserver_pipe: ", multiServer_pipe)
    #curProcPID = multiServer_pipe.recv()
    #curProcSeqID = multiServer_pipe.recv()

    webserviceMsg = multiServer_pipe.recv()
    handlerID = multiServer_pipe.recv()
    seqID = multiServer_pipe.recv()

    #webserviceMsg = (curProcPID, curProcSeqID)
    #print("PID: %d, SeqID: %d" % (webserviceMsg[0], webserviceMsg[1]))
    print("webserviceMsg: ", webserviceMsg, " handlerID: ", handlerID, " seqID: ", seqID)
    return webserviceMsg


def pid_handler(webservice_pipe, argsList):
    sendMsgsToMultiServer(webservice_pipe, argsList)

Pipes = list()


class PreforkedHybridMultiServer:

    def __init__(self, handlersList, handlersArgsList, poolTasksTimeout=None, poolShoutdownTimeout=300, AMDAHLS_COEFFICIENT=2):
        # dispathingSupervisor = mp.Manager()
        # generalLock = mp.Lock()
        self.WEBSERVICES_MAX_COUNT = len(handlersList)
        self.POOL_SIZE = AMDAHLS_COEFFICIENT * mp.cpu_count()
        self._ppeWorkers = concurrent.futures.ProcessPoolExecutor(max_workers=self.POOL_SIZE)
        self._ppeRecvPipeWorkers = concurrent.futures.ProcessPoolExecutor(max_workers=self.WEBSERVICES_MAX_COUNT)
        self._futuresTasks = list()
        self._poolTasksTimeout = poolTasksTimeout
        self._poolShoutdownTimeout = poolShoutdownTimeout
        # endpoints for IPC (Coordinator and web-services)
        self._pipes = []
        self.ipcEndpointsCreate()
        # the list of handlers for scheduler
        self._handlersList = handlersList
        # the list of handlers args
        self._handlersArgsList = handlersArgsList
        # working Proc PID and task
        self._generalList = list()

    def ipcEndpointsCreate(self):
        #self._pipes.clear()
        for i in range(0, self.WEBSERVICES_MAX_COUNT):
            parent_conn, child_conn = Pipe()
            self._pipes.append( (parent_conn, child_conn) )
            Pipes.append( (parent_conn, child_conn) )
        # make pipes global visible
        #Pipes = list(self._pipes)
        #Pipes.append(self._pipes[i])
        print("Glogal Visible Pipes:")
        print(Pipes)

    def processPoolExecutorMonitoringStatus(self):
        '''
            return_when=
            FIRST_COMPLETED 	The function will return when any future finishes or is cancelled.
            FIRST_EXCEPTION 	The function will return when any future finishes by raising an exception. If no future raises an exception then it is equivalent to ALL_COMPLETED.
            ALL_COMPLETED 	The function will return when all futures finish or are cancelled.
        '''
        fsTasksAreDone, fsTasksAreNotDone = concurrent.futures.wait(self._futuresTasks,
                                                                    timeout=self._poolShoutdownTimeout,
                                                                    return_when=concurrent.futures.ALL_COMPLETED)
        print("LOG: Tasks that have been finished successfully:")
        print(fsTasksAreDone)
        print("LOG: Tasks that have not been finished:")
        print(fsTasksAreNotDone)

    def dispatheringScheduler(self, executors):
        # futuresTasks = [executors.map(f, (num, generalLock)) for num in range(3)]
        for i in range(0, self.WEBSERVICES_MAX_COUNT):
            self._handlersArgsList[i].append(i)
            self._futuresTasks.append(
                executors.submit(self._handlersList[i], self._pipes[i][1], self._handlersArgsList[i]))
            curProcPID = os.getpid()
            self._generalList.append(([curProcPID, i], self._futuresTasks[i]))

    def getCallableResultsFromFS(self):
        # for futureTask in concurrent.futures.as_completed(futuresTasks):
        for finishedTask in concurrent.futures.as_completed(self._futuresTasks, timeout=self._poolTasksTimeout):
            # finishedTask = futuresTasks[futureTask]
            try:
                # print('working proc in procPoolExecutors : %d, PID: %d and result: %d' % (0, 0, finishedTask.result()))
                print(finishedTask.result())
            except Exception as exc:
                print('LOG: web-service future struct: %r generated an exception: %s' % (finishedTask, exc))
            # except concurrent.futures.BrokenProcessPool as brkProcErr:
            except concurrent.futures.CancelledError as cnclErr:
                print(
                    "LOG: Error! One or more of the workers of a ProcessPoolExecutor has cancelled or terminated in a non-clean fashion (for example, if it was killed from the outside)")
                print(cnclErr)
            except TimeoutError as tmoutErr:
                print("LOG: We lacked patience and got a multiprocessing.TimeoutError")
                print(tmoutErr)
            finally:
                print("Success iteration")

    def poolCorrectShutdown(self, executors):
        self.processPoolExecutorMonitoringStatus()
        executors.shutdown(wait=True)

    def run(self):
        startTime = timer()
        with self._ppeWorkers as executors:
            # task scheduling
            self.dispatheringScheduler(executors)
            # get results from callable type executors (futures struct)
            self.getCallableResultsFromFS()
            # pool turn off
            self.poolCorrectShutdown(executors)
        endTime = timer() - startTime
        print("LOG: processing time: ", endTime)

    def recvWebServicesMsgs(self):
        futuresTasks = list()
        with self._ppeRecvPipeWorkers as executors:
            for i in range(0, self.WEBSERVICES_MAX_COUNT):
                #futuresTasks.append(executors.map(recvWebServiceMsg, self._pipes[i][0]))
                #print("Global Pipe: ", Pipes[i][0])
                #futuresTasks.append(executors.map(recvWebServiceMsg, Pipes[i][0]))
                futuresTasks.append(executors.map(recvWebServiceMsg, Pipes[i]))
            #for i, result in zip(self._pipes, futuresTasks):
            for i, result in zip(Pipes, futuresTasks):
                # futuresTasks.append(executors.map(f, num[i], generalLock))
                #print("communication pipes pair :", i, "; msg: [", result[0], ", ", result[1], ", ", result[2], "]")
                print("communication pipes pair :", i, "; msg: [", result, "]")


if __name__ == '__main__':
    #create MultiServer
    handlers = [ pid_handler, pid_handler, pid_handler ]
    #handlers = list()
    #handlers.append(sendMsgsToMultiServer)
    handlers_args = list()

    for i in range(0, len(handlers)):
        handler_args = list()
        handler_args.append(i)
        handlers_args.append(handler_args)

    phMultiServer = PreforkedHybridMultiServer(handlers, handlers_args)
    phMultiServer.run()
    # test for IPC
    phMultiServer.recvWebServicesMsgs()