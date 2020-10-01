#!/usr/bin/env python3
from b2handle.clientcredentials import PIDClientCredentials
from b2handle.handleclient import EUDATHandleClient

cred = PIDClientCredentials.load_from_JSON('credentials.json')
client = EUDATHandleClient.instantiate_with_credentials(cred)
