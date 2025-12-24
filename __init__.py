from . import Print

def getMetaData():
    return {}

def register(app):
    return {"extension": Print.Print()}
