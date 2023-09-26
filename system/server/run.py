from src import app
from flask import Flask,request
from flask_cors import CORS
# app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)
# hostIP='10.192.9.11'
# portId=8090
# @app.route("/")
# def hello_world():
#     if request.remote_addr.startswith('10.') or request.remote_addr.startswith('localhost'):
#         host = '10.192.9.11'
#     else:
#         host = '103.21.143.204'
#     app.run(host=host, port=5055, use_reloader=True, debug=True)
#     return "Hello, World!"

# if __name__ == "__main__":
#     print(host)
# if request.remote_addr.startswith('10.') or request.remote_addr.startswith('localhost'):
#     hostIP = '10.192.9.11'
#     portId=8090
# else:
#     hostIP = '124.220.133.205'
#     portId=41090
# print('IP Address:',hostIP)
# print('Port:',portId)
app.run(host='0.0.0.0', port=8090, use_reloader=True, debug=True)
# app.run(host=host, port=5055, use_reloader=True, debug=True)