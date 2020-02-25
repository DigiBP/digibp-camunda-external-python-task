import cam
import random

worker = cam.client("https://digibp.herokuapp.com/rest")

def getSurpriseMenuCallback(body):
    try:
        vegetarianGuests = print(body[0]['variables']['vegetarianGuests']['value'])
    except:
        vegetarianGuests = False
        
    if vegetarianGuests:
        menu = random.choice(["pizza", "pasta", "verdura"])
    else:
        menu = random.choice(["pizza", "pasta", "carne", "verdura"])
        
    variables = {"menu": menu}
    worker.complete(body, **variables)

worker.subscribe("GetSurpriseMenu", getSurpriseMenuCallback, "showcase")

worker.polling()