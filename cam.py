import requests
import json
import time
import threading
import uuid

class client:
    def __init__(self, url, workerid=None):
        self.url = url
        self.workerid = workerid
        self.threads=[]

    def __fetch_and_lock(self, endpoint, task, callback):
        body = '[]'

        try:
            while True:
                print("polling")
                fetch_and_lock = requests.post(endpoint, json=task)
                print(fetch_and_lock.status_code)
                body = fetch_and_lock.text
                if body != '[]':
                    if callback:
                        callback(json.loads(body))
                    else:
                        break
                else:
                    time.sleep(5)
        except:
            print("Engine is down")

    def subscribe(self, topic, callback, tenantId=None, lockDuration=1000, longPolling=5000):
        # Define the endpoint for fetch and lock
        endpoint = str(self.url) + "/external-task/fetchAndLock"
        
        # Define unique ID for the worker, if undifiend
        if self.workerid:
            workerid = str(self.workerid)
        else:
            global uid
            uid = uuid.uuid1()
            workerid = str(uid)

        if tenantId:
            task = {"workerId": workerid,
                    "maxTasks": 1,
                    "usePriority": "true",
                    "asyncResponseTimeout": longPolling,
                    "topics":
                        [{"topicName": topic,
                          "lockDuration": lockDuration,
                          "tenantIdIn": [
                              tenantId
                          ]
                          }]
                    }
        else:
            task = {"workerId": workerid,
                    "maxTasks": 1,
                    "usePriority": "true",
                    "asyncResponseTimeout": longPolling,
                    "topics":
                        [{"topicName": topic,
                          "lockDuration": lockDuration
                          }]
                    }

        self.threads.append(threading.Thread(target=self.__fetch_and_lock, args=(endpoint, task, callback, )))

    def polling(self):
        for thread in self.threads:
            thread.start()
        while True:
            pass

    # Complete Call
    def complete(self, response_body, **kwargs):
        taskid = response_body[0]['id']
        taskid = str(taskid)

        endpoint = str(self.url) + "/external-task/" + taskid + "/complete"

        # get workerid
        workerid = response_body[0]['workerId']
        workerid = str(workerid)

        # puts the variables from the dictonary into the nested format for the json response
        variables_for_response = {}
        for key, val in kwargs.items():
            variable_new = {key: {"value": val}}
            variables_for_response.update(variable_new)

        response = {"workerId": workerid,
                    "variables": variables_for_response
                    }

        try:
            complete = requests.post(endpoint, json=response)
            body_complete = complete.text
            print(body_complete)
            print(complete.status_code)

        except:
            print('fail')

    # BPMN Error
    def error(self, bpmn_error, response_body, error_message="not defined", **kwargs):
        taskid = response_body[0]['id']
        taskid = str(taskid)

        endpoint = str(self.url) + "/external-task/" + taskid + "/bpmnError"

        workerid = response_body[0]['workerId']
        workerid = str(workerid)

        variables_for_response = {}
        for key, val in kwargs.items():
            variable_new = {key: {"value": val}}
            variables_for_response.update(variable_new)

        response = {
            "workerId": workerid,
            "errorCode": bpmn_error,
            "errorMessage": error_message,
            "variables": variables_for_response
        }

        try:
            error = requests.post(endpoint, json=response)
            print(error.status_code)

        except:
            print('fail')

    # Create an incident
    def fail(self, error_message, response_body, retries=0, retry_timeout=0):
        taskid = response_body[0]['id']
        taskid = str(taskid)

        endpoint = str(self.url) + "/external-task/" + taskid + "/failure"

        workerid = response_body[0]['workerId']
        workerid = str(workerid)

        response = {
            "workerId": workerid,
            "errorMessage": error_message,
            "retries": retries,
            "retryTimeout": retry_timeout}

        try:
            fail = requests.post(endpoint, json=response)
            print(fail.status_code)

        except:
            print('fail')

    # New Lockduration           
    def new_lockduration(self, new_duration, response_body):
        taskid = response_body[0]['id']
        taskid = str(taskid)

        endpoint = str(self.url) + "/external-task/" + taskid + "/extendLock"

        workerid = response_body[0]['workerId']
        workerid = str(workerid)

        response = {
            "workerId": workerid,
            "newDuration": new_duration
        }

        try:
            newDuration = requests.post(endpoint, json=response)
            print(newDuration.status_code)
            print(workerid)
        except:
            print('fail')