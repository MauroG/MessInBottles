from flask import Flask, send_from_directory, request, abort
import os.path
app = Flask(__name__)


# Make the WSGI interface available at the top level so wfastcgi can get it.
# wsgi_app = app.wsgi_app # It's useful in any way?


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

# Uncomment the 2 lines below to run this "app.py" and avoid to use bootstrap.bat or equivalent bootstrap.sh
# if __name__ == '__main__':
#   app.run(port=5000, debug=True)
