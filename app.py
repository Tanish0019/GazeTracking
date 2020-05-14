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
    focused_frames = calc_video_focus(url=url, video_id=video_id, debug=False)
    if focused_frames<=0:
        message = 'Eyes were not detected. Please follow the instructions properly.'
    else:
        time_focused = focused_frames/2
        print(f"time_focused: {time_focused} seconds")
        message = f'You were focused for {time_focused} seconds.' 
    return jsonify({"msg": message}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
