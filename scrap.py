#!/usr/bin/env python
import requests
import pika
import sys
from bs4 import BeautifulSoup

urls = {'phoenix': 'http://www.court-records.net/animation/aa-phoenix.htm', 'edgeworth': 'http://www.court-records.net/animation/aa-edgeworth.htm', 'vonkarma': 'http://www.court-records.net/animation/aa-fran.htm', 'godot': 'http://www.court-records.net/animation/aa-godot.htm'}
general_url = 'http://www.court-records.net/animation/'
#message = 'hola que tal'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

for url in urls.values():
	result = requests.get(url)
	soup = BeautifulSoup(result.text, "html.parser")
	
	for i in soup.findAll('img'):
		if (i['src'].find(".gif") >= 0 and (
			i['src'].find("zoom") >= 0 or
			i['src'].find("objection") >= 0 or
			i['src'].find("desk") >= 0 or
			i['src'].find("pointing") >= 0 or
			i['src'].find("headshake") >= 0 or
			i['src'].find("objecting") >= 0)):
				channel.basic_publish(exchange='logs', routing_key='', body=general_url + i['src'])
				print(' [x] Solicitando imagen desde |', i['src'], '|')# %r" % message)

connection.close()