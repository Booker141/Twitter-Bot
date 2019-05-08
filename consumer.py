#!/usr/bin/env python
import pika
import time
import dropbox
import tempfile
import requests
import tweepy
import pandas
import datetime

consumer_key = "Q7TFCe2gqcAE5RM9WFvVaFYDd"								
consumer_secret = "EaqfCCVd7qCLy2ZmJpseeZJ9afyrN6YxdfLfXVEdgKwvxEaLqz"	
access_token = "1110972023143124992-MeI7xrqFmib6m8QtLLF2nrdzYfHYqj"		
access_token_secret = "RjYDSw5es3R7Sf38eAcQ1gMscxYXTFk6vB4qd44p59zgl"	

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)	
auth.set_access_token(access_token, access_token_secret)	
api = tweepy.API(auth)

token = '2LSGMO_SETAAAAAAAAAAEGFCm9QjaipYWYV9P484x-7OqfSf-sEDibbSn5bKNiRz'
dbx = dropbox.Dropbox(token)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare('pics')
channel.queue_declare('tweets')

print('[*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
	print('[x] Imagen solicitada: |', body.decode(), '|')
	
	r = requests.get(body)
	components = body.decode().split('/')
	name = components[len(components)-1]
	
	print('[*] Subiendo imagen...')
	data = r.content
	dbx.files_upload(data, '/'+name, mute=True)
	
	time.sleep(2)
	print("[*] Listo.")
	
def callback2(ch, method, properties, body):
	st=api.get_status(int(body))
	print("[*] Solicitud de almacenamiento del tweet con ID = ", body)
	excel = tempfile.NamedTemporaryFile(suffix=".xls", delete=False)
	froute = excel.name		#Ruta del fichero temporal
	dbx.files_download_to_file(froute, "/stadistics.xls")	#Guardamos el .xls en el fichero temporal
	print("[*] Generado archivo temporal "+froute)
	df = pandas.read_excel(froute, sheet_name=0)	#Cargamos el excel en un DataFrame
		
	fllws = []
	for page in tweepy.Cursor(api.followers_ids, id=st.user.id).pages():	#Recorre los followers
		fllws.extend(page)
		time.sleep(0.05)	#Pausa mínima de precaución para las peticiones
	
	newrow = pandas.DataFrame(data={'ID': [str(body)], 'Tweet': [st.text], 'Autor': ["@"+st.user.screen_name], 'Seguidores': [len(fllws)], 'Fecha': [str(datetime.datetime.now())]})	#Creamos un DataFrame con la nueva tupla a añadir
	print("[*] Registrando tweet... ")
	df = pandas.concat([df, newrow], join='inner')	#Concatenamos ambos DataFrame
	print("[*] Guardando los cambios...")
	df.to_excel(froute)	#Guardamos cambios en el fichero
	with open(froute, 'rb') as f:
		data = f.read()
	dbx.files_upload(data, '/stadistics.xls', mode=dropbox.files.WriteMode.overwrite, mute=True)	#Lo resubimos a dropbox
	print("[*] El archivo |/stadistics.xls| ha sido actualizado.")

channel.basic_consume(queue='pics', on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue='tweets', on_message_callback=callback2, auto_ack=True)

channel.start_consuming()