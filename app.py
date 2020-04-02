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
    focus = calc_video_focus(url)

    if focus == -1:
        return jsonify({
            "success": False,
            "message": "Please make sure you're looking at the dot when you start the video."
        })

    return jsonify({"score": focus})


if __name__ == "__main__":
    app.run(port=4555, debug=True)
