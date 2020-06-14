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
    first_time,focused_frames,duration = calc_video_focus(url=url, video_id=video_id, debug=False)
    if focused_frames<=0:
        message = 'Eyes were not detected. Please follow the instructions properly.'
        duration_str = ''
        first_str = ''
    else:
        if first_time==-1:
            focused_frames = duration
            first_str = "You were focused throughout the experiment"
        else:
            first_str = f"You first lost your focus at {first_time} seconds"
        print(f"time_focused: {time_focused} seconds and total duration: {duration}")
        message = f'You were focused for {time_focused} seconds.' 
        duration_str = f'The video was {duration} seconds long.'
        
    return jsonify({"msg": message,"duration": duration_str,"first": first_str}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
