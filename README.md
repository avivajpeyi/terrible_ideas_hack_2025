# Terrible ideas Hack '25

https://terrible-ideas-5-tamaki-makaurau.lilregie.com/


## Requirements:
1. Python 3.10/11 (NOT 3.13)
2. Webcam
3. Arduino uno (optional)

The code 
python 3.10/.11

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
wget -O pose_landmarker.task -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task
```


### Arduino setup
We have a ESP8266 board. We need to get it to work with the Arduino IDE.

https://www.instructables.com/ESP8266-and-Python-Communication-ForNoobs/

