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

    def __fetch_and_lock(self, endpoint, task, callback=None, interval=300):
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
                        return json.loads(body)
                else:
                    time.sleep(interval / 1000)

        except:
            print("Engine is down")

    def subscribe(self, topic, callback=None, tenantId=None, lockDuration=20000, longPolling=29000):
        # Define the endpoint for fetch and lock
        endpoint = str(self.url) + "/external-task/fetchAndLock"

        if tenantId:
            task = {"workerId": self.workerid,
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
            task = {"workerId": self.workerid,
                    "maxTasks": 1,
                    "usePriority": "true",
                    "asyncResponseTimeout": longPolling,
                    "topics":
                        [{"topicName": topic,
                          "lockDuration": lockDuration
                          }]
                    }
        if callback:
            self.threads.append(threading.Thread(target=self.__fetch_and_lock, args=(endpoint, task, callback,)))
        else:
            return self.__fetch_and_lock(endpoint, task)

    def polling(self):
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

    # Complete Call
    def complete(self, response_body, **kwargs):
        taskid = str(response_body[0]['id'])

        endpoint = str(self.url) + "/external-task/" + taskid + "/complete"

        # puts the variables from the dictonary into the nested format for the json response
        variables_for_response = {}
        for key, val in kwargs.items():
            variable_new = {key: {"value": val}}
            variables_for_response.update(variable_new)

        response = {"workerId": self.workerid,
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
        taskid = str(response_body[0]['id'])

        endpoint = str(self.url) + "/external-task/" + taskid + "/bpmnError"

        variables_for_response = {}
        for key, val in kwargs.items():
            variable_new = {key: {"value": val}}
            variables_for_response.update(variable_new)

        response = {
            "workerId": self.workerid,
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
        taskid = str(response_body[0]['id'])

        endpoint = str(self.url) + "/external-task/" + taskid + "/failure"

        response = {
            "workerId": self.workerid,
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
        taskid = str(response_body[0]['id'])

        endpoint = str(self.url) + "/external-task/" + taskid + "/extendLock"

        response = {
            "workerId": self.workerid,
            "newDuration": new_duration
        }

        try:
            newDuration = requests.post(endpoint, json=response)
            print(newDuration.status_code)
            print(self.workerid)
        except:
            print('fail')
