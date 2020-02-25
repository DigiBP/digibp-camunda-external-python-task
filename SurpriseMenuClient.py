import cam
import random

worker = cam.Client("https://digibp.herokuapp.com/rest")


def get_surprise_menu_callback(body):
    try:
        vegetarian_guests = body[0]['variables']['vegetarianGuests']['value']
    except:
        vegetarian_guests = False

    if vegetarian_guests:
        menu = random.choice(["pizza", "pasta", "verdura"])
    else:
        menu = random.choice(["pizza", "pasta", "carne", "verdura"])

    variables = {"menu": menu}
    worker.complete(body, **variables)


worker.subscribe("GetSurpriseMenu", get_surprise_menu_callback, "showcase")

worker.polling()
