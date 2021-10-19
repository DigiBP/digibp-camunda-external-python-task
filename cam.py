import requests
import json
import time
import threading
import uuid


class Client:
    def __init__(self, url, workerid=None):
        self.url = url
        if workerid:
            self.workerid = str(workerid)
        else:
            self.workerid = str(uuid.uuid1())
        self.threads = []
        self.stop_event = threading.Event()

    def __fetch_and_lock(self, endpoint, task, callback=None, interval=300):
        try:
            while not self.stop_event.isSet():
                print("polling subscription: " + task["topics"][0]["topicName"])
                response = requests.post(endpoint, json=task)
                print(response.status_code)
                response = response.text
                if response != '[]':
                    response = json.loads(response)
                    taskid = str(response[0]['id'])
                    if callback:
                        callback(taskid, response)
                    else:
                        return response
                else:
                    time.sleep(interval / 1000)

        except:
            print("fail - subscription cancelled: " + task["topics"][0]["topicName"])

    def subscribe(self, topic, callback=None, tenantId=None, lockDuration=20000, longPolling=29000):
        endpoint = str(self.url) + "/external-task/fetchAndLock"

        task = {"workerId": self.workerid,
                "maxTasks": 1,
                "usePriority": "true",
                "asyncResponseTimeout": longPolling,
                "topics":
                    [{"topicName": topic,
                        "lockDuration": lockDuration,
                        "tenantIdIn" if tenantId else None: [tenantId]
                        }]
                }

        if callback:
            self.threads.append(threading.Thread(target=self.__fetch_and_lock, args=(endpoint, task, callback,)))
        else:
            return self.__fetch_and_lock(endpoint, task)

    def polling(self):
        try:
            for thread in self.threads:
                if not self.stop_event.isSet():
                    thread.start()
            for thread in self.threads:
                if thread.isAlive():
                    thread.join()
                if self.stop_event.isSet():
                    self.threads = []
                    self.stop_event.clear()
                    print("stopped - you may need to subscribe again")
        except KeyboardInterrupt:
            self.stop_event.set()

    # Complete Call
    def complete(self, taskid, **kwargs):
        endpoint = str(self.url) + "/external-task/" + taskid + "/complete"

        # puts the variables from the dictonary into the nested format for the json response
        variables_for_response = {}
        for key, val in kwargs.items():
            variable_new = {key: {"value": val}}
            variables_for_response.update(variable_new)

        request = {"workerId": self.workerid,
                    "variables": variables_for_response
                    }

        try:
            response = requests.post(endpoint, json=request)
            body_complete = response.text
            print(body_complete)
            print(response.status_code)

        except:
            print('fail')

    # BPMN Error
    def error(self, bpmn_error, taskid, error_message="not defined", **kwargs):
        endpoint = str(self.url) + "/external-task/" + taskid + "/bpmnError"

        variables_for_response = {}
        for key, val in kwargs.items():
            variable_new = {key: {"value": val}}
            variables_for_response.update(variable_new)

        request = {
            "workerId": self.workerid,
            "errorCode": bpmn_error,
            "errorMessage": error_message,
            "variables": variables_for_response
        }

        try:
            response = requests.post(endpoint, json=request)
            print(response.status_code)

        except:
            print('fail')

    # Create an incident
    def fail(self, error_message, taskid, retries=0, retry_timeout=0):
        endpoint = str(self.url) + "/external-task/" + taskid + "/failure"

        request = {
            "workerId": self.workerid,
            "errorMessage": error_message,
            "retries": retries,
            "retryTimeout": retry_timeout}

        try:
            response = requests.post(endpoint, json=request)
            print(response.status_code)

        except:
            print('fail')

    # New Lockduration
    def new_lockduration(self, new_duration, taskid):
        endpoint = str(self.url) + "/external-task/" + taskid + "/extendLock"

        request = {
            "workerId": self.workerid,
            "newDuration": new_duration
        }

        try:
            response = requests.post(endpoint, json=request)
            print(response.status_code)
            print(self.workerid)
        except:
            print('fail')
