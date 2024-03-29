import cam
import random


class SurpriseMenuClient:
    def __init__(self):
        self.worker = cam.Client("https://digibp.herokuapp.com/engine-rest")
        self.worker.subscribe("GetSurpriseMenu", self.get_surprise_menu_callback, "showcase")
        self.worker.polling()

    def get_surprise_menu_callback(self, taskid, response):
        try:
            vegetarian_guests = response[0]['variables']['vegetarian']['value']
        except:
            vegetarian_guests = False

        if vegetarian_guests:
            menu = random.choice(["pizza", "pasta", "verdura"])
        else:
            menu = random.choice(["pizza", "pasta", "carne", "verdura"])

        variables = {"menu": menu}
        self.worker.complete(taskid, **variables)


if __name__ == '__main__':
    SurpriseMenuClient()
