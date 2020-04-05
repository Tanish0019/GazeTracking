from flask import Flask, request, jsonify
import werkzeug
import time
from eye_tracker import calc_video_focus

app = Flask(__name__)


@app.route('/', methods=['GET'])
def check():
    return 'OK'


@app.route('/post', methods=['POST'])
def video_focus():
    param = request.get_json()
    url = param["url"]
    print(url)
    focus = calc_video_focus(url, frame_freq=10, threshold=0.07)
    print(f"Focus: {focus}")
    return jsonify({"score": focus})


if __name__ == "__main__":
    app.run(port=4555, debug=True)
