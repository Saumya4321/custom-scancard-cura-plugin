from . import PrintController

def getMetaData():
    return {}

def register(app):
    return {"extension": PrintController.PrintController()}
