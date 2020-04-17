import os
from flask import Flask, request, jsonify
import werkzeug
from eye_tracker import calc_video_focus

app = Flask(__name__)


@app.route('/', methods=['GET'])
def check():
    return 'OK'


@app.route('/post', methods=['POST'])
def video_focus():
    content = request.get_json()
    url = content["url"]
    video_id = content["video_id"]
    print("flask: ", url, video_id)
    focus = calc_video_focus(url=url, video_id=video_id, debug=False)
    print(f"Focus: {focus}")
    return jsonify({"score": focus}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
