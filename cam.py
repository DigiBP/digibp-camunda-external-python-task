import requests
import json
import time
import threading
import uuid
import logging

logging.basicConfig(level=logging.INFO)

class Client:
    def __init__(self, url, workerid=None):
        self.url = url
        self.workerid = str(workerid) if workerid else str(uuid.uuid1())
        self.threads = []
        self.stop_event = threading.Event()

    def __fetch_and_lock(self, endpoint, task, callback=None, interval=300):
        try:
            while not self.stop_event.is_set():
                logging.info(f"Polling subscription: {task['topics'][0]['topicName']}")
                response = requests.post(endpoint, json=task)
                logging.info(f"Response status: {response.status_code}")
                
                response_text = response.text
                if response_text != '[]':
                    response_data = json.loads(response_text)
                    taskid = str(response_data[0]['id'])
                    
                    # Log task ID and variables pulled
                    task_variables = response_data[0].get('variables', {})
                    logging.info(f"Task fetched with ID: {taskid} and data: {task_variables}")
                    
                    if callback:
                        callback(taskid, response_data)
                    else:
                        return response_data
                else:
                    time.sleep(interval / 1000)

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for subscription: {task['topics'][0]['topicName']}, error: {e}")

    def subscribe(self, topic, callback=None, tenantId=None, lockDuration=20000, longPolling=29000):
        endpoint = f"{self.url}/external-task/fetchAndLock"
        task = {
            "workerId": self.workerid,
            "maxTasks": 1,
            "usePriority": "true",
            "asyncResponseTimeout": longPolling,
            "topics": [{
                "topicName": topic,
                "lockDuration": lockDuration,
            }]
        }
        if tenantId:
            task['topics'][0]['tenantIdIn'] = [tenantId]

        if callback:
            self.threads.append(threading.Thread(target=self.__fetch_and_lock, args=(endpoint, task, callback,)))
        else:
            return self.__fetch_and_lock(endpoint, task)

    def polling(self):
        try:
            for thread in self.threads:
                if not self.stop_event.is_set():
                    thread.start()
            for thread in self.threads:
                if thread.is_alive():
                    thread.join()
                if self.stop_event.is_set():
                    self.threads = []
                    self.stop_event.clear()
                    logging.info("Stopped - you may need to subscribe again")
        except KeyboardInterrupt:
            self.stop_event.set()

    def complete(self, taskid, **kwargs):
        endpoint = f"{self.url}/external-task/{taskid}/complete"
        variables_for_response = {key: {"value": val} for key, val in kwargs.items()}

        request = {
            "workerId": self.workerid,
            "variables": variables_for_response
        }

        try:
            response = requests.post(endpoint, json=request)
            if response.status_code == 204:
                logging.info(f"Task {taskid} completed successfully with data: {request}")
            else:
                logging.info(f"Response: {response.text}, Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")

    def error(self, taskid, error_code, error_message="not defined", **kwargs):
        endpoint = f"{self.url}/external-task/{taskid}/bpmnError"
        variables_for_response = {key: {"value": val} for key, val in kwargs.items()}

        request = {
            "workerId": self.workerid,
            "errorCode": error_code,
            "errorMessage": error_message,
            "variables": variables_for_response
        }

        try:
            response = requests.post(endpoint, json=request)
            logging.info(f"Error response: {response.text}, Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")

    def failure(self, taskid, error_message="not defined", retries=0, retry_timeout=0):
        endpoint = f"{self.url}/external-task/{taskid}/failure"
        request = {
            "workerId": self.workerid,
            "errorMessage": error_message,
            "retries": retries,
            "retryTimeout": retry_timeout
        }

        try:
            response = requests.post(endpoint, json=request)
            logging.info(f"Failure response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")

    def extend_lock(self, taskid, new_duration):
        endpoint = f"{self.url}/external-task/{taskid}/extendLock"
        request = {
            "workerId": self.workerid,
            "newDuration": new_duration
        }

        try:
            response = requests.post(endpoint, json=request)
            logging.info(f"Extended lock for task {taskid} with response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
