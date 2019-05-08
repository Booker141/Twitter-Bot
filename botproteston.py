#!/usr/bin/env python
import tweepy
import pika
import random
import time
import dropbox
import sys
import tempfile

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs')

consumer_key = "Q7TFCe2gqcAE5RM9WFvVaFYDd"								#
consumer_secret = "EaqfCCVd7qCLy2ZmJpseeZJ9afyrN6YxdfLfXVEdgKwvxEaLqz"	# Claves de acceso
access_token = "1110972023143124992-MeI7xrqFmib6m8QtLLF2nrdzYfHYqj"		# a Twitter
access_token_secret = "RjYDSw5es3R7Sf38eAcQ1gMscxYXTFk6vB4qd44p59zgl"	#

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)	# Acceso a la cuenta
auth.set_access_token(access_token, access_token_secret)	# de Twitter
api = tweepy.API(auth)										#

token = '2LSGMO_SETAAAAAAAAAAEGFCm9QjaipYWYV9P484x-7OqfSf-sEDibbSn5bKNiRz'	# Clave de acceso
dbx = dropbox.Dropbox(token)												# a Dropbox

files = dbx.files_list_folder("")	#Lista de directorios y ficheros en Dropbox
if (len(files.entries) <= 1):	#Finaliza la ejecución si no hay ficheros
	print("Dropbox no contiene archivos")
	sys.exit(0)
while (files.has_more):		#Si hay varias páginas de ficheros, se cargan todos
	files2 = dbx.files_list_folder_continue(files.cursor)
	files = files + files2
for f in files.entries:		#Se recorren los ficheros descartando los que no sean .gif
	if (".gif" not in f.name):
		files.entries.remove(f)

class MyStreamListener(tweepy.StreamListener):	#Clase de configuración del StreamListener
	def get_image(self):
		giffile = random.choice(files.entries)	#Se elige al azar un gif de la lista
		path = "/"+giffile.name
		print("[*] Obteniendo imagen "+giffile.name+" de Dropbox...")
		image = tempfile.NamedTemporaryFile(suffix=".gif", delete=False) #Almacenamiento
		dbx.files_download_to_file(image.name, path)	#Descarga en el fichero anterior
		print("[*] Imagen almacenada de forma temporal con nombre "+image.name.split('\\')[-1])
		return image.name
		
	def on_status(self, status):
		if ("RT @" not in status.text and
			"gobierno" not in status.text and				# Filtrado de tweets a responder
			"venezuela" not in status.text and
			status.user.screen_name != "tu_invernadero"):
			
			print("[*] Detectado: " + status.text + " || de @" + status.user.screen_name)
			img = self.get_image()
			mediaid=api.media_upload(img)	#Subida al servidor de twitter
			print("[*] Imagen subida al servidor de Twitter.")
			time.sleep(5)
			api.update_status("@"+status.user.screen_name+" PROTESTO! ",	#Responde al tweet detectado
							 in_reply_to_status_id=status.id,	#mencionando al autor y
							 media_ids=[mediaid.media_id])		#añadiendo el gif elegido
			print("[*] Respondido. Realizando petición al servidor para almacenar el tweet...")
			channel.basic_publish(exchange='', routing_key='tweets', body=str(status.id))
			time.sleep(3)
			print("[*] Petición enviada. Listo para cargar el siguiente tweet.")
		
streamListener = MyStreamListener()
tweets = tweepy.Stream(auth=api.auth, listener=streamListener)	#Creación del stream
tweets.filter(track=['protesto', 'protestando', 'protestar', 'protestado', 'protestooo', 'Phoenix Wright', 'Ace Attorney'], languages=['es'], is_async=True)	#Parámetros de búsqueda