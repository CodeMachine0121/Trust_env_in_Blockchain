import time

def emptySessionKey(client):
    client["sk"]=-1
    client['Chash'].x = -1
    client['Chash'].y = -1
    return client

def ifSessionKeyEmpty(client):
    if client["sk"]!=-1 and client["Chash"].x!=-1 and client["Chash"].y!=-1:
        return True
    else:
        return False

def ifSessionKey_outDate(startTime):
    if time.time() - startTime > 10:
        return True
    else:
        return False

