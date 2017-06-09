from flask import Flask, send_from_directory, request, abort
import os.path
app = Flask(__name__)

@app.route('/api/<path:path>', methods = ["GET", "POST"])
def api(path=None):
	if request.method == "POST":
		print('post received')
		print(request.data)
	if request.method == "GET":
		print('it works')
	abort(400)

@app.route('/')
@app.route('/<path:path>')
def sendPureHTML(path=None):
	print(os.path.dirname(os.path.realpath(__file__)))
	if path is None:
		return send_from_directory('templates', 'index.html')
	elif os.path.isfile(os.path.dirname(os.path.realpath(__file__))+'/templates/'+path):
		return send_from_directory('templates', path)
	else:
		return send_from_directory('templates', 'index.html')
