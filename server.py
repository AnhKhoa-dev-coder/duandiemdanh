# from flask import send_from_directory
# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import face_recognition
# import numpy as np
# import base64
# import cv2
# import pickle
# from datetime import datetime
# IMAGE_DIR = "storage"
# @app.route("/storage/<filename>")
# def get_image(filename):
#     return send_from_directory(IMAGE_DIR, filename)

# app = Flask(__name__)
# CORS(app)

# # ================== DỮ LIỆU CỐ ĐỊNH ==================
# USERS = {
#     "1112": {
#         "name": "XA ANH KHOA",
#         "class": "11A1",
#         "encoding_index": 0   # index trong encodings.pickle
#     }
# }

# DATA_FILE = "attendance.csv"

# # Load encoding khuôn mặt
# with open("encodings.pickle", "rb") as f:
#     data = pickle.load(f)

# # ================== API ĐIỂM DANH ==================
# @app.route("/attendance", methods=["POST"])
# def attendance():
#     req = request.json
#     code = req.get("code")
#     img_data = req.get("image")

#     if code not in USERS:
#         return jsonify({"status": "fail", "message": "Mã không hợp lệ"})

#     # Decode ảnh
#     img_bytes = base64.b64decode(img_data.split(",")[1])
#     np_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
#     rgb = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

#     boxes = face_recognition.face_locations(rgb)
#     encodings = face_recognition.face_encodings(rgb, boxes)

#     if len(encodings) == 0:
#         return jsonify({"status": "fail", "message": "Không phát hiện khuôn mặt"})

#     user = USERS[code]
#     known_encoding = data["encodings"][user["encoding_index"]]

#     dist = face_recognition.face_distance([known_encoding], encodings[0])[0]
#     accuracy = (1 - dist) * 100

#     if dist > 0.5:
#         return jsonify({
#             "status": "fail",
#             "accuracy": round(accuracy, 2)
#         })

#     now = datetime.now()
#     with open(DATA_FILE, "a", encoding="utf-8") as f:
#         f.write(f"{code},{user['name']},{user['class']},{now.date()},{now.strftime('%H:%M:%S')}\n")

#     return jsonify({
#         "status": "success",
#         "name": user["name"],
#         "class": user["class"],
#         "accuracy": round(accuracy, 2)
#     })


# # ================== DANH SÁCH HÔM NAY ==================
# @app.route("/today")
# def today():
#     result = []
#     today = str(datetime.now().date())

#     try:
#         with open(DATA_FILE, "r", encoding="utf-8") as f:
#             for line in f:
#                 code, name, cls, date, time = line.strip().split(",")
#                 if date == today:
#                     result.append({
#                         "code": code,
#                         "name": name,
#                         "class": cls,
#                         "date": date,
#                         "time": time
#                     })
#     except FileNotFoundError:
#         pass

#     return jsonify(result)


# if __name__ == "__main__":
#     app.run(debug=True)
# @app.route("/search/<code>")
# def search(code):
#     if not os.path.exists(DATA_FILE):
#         return jsonify({"status": "fail"})

#     last_row = None

#     with open(DATA_FILE, "r", encoding="utf-8") as f:
#         for line in f:
#             c, name, cls, date, time = line.strip().split(",")
#             if c == code:
#                 last_row = {
#                     "code": c,
#                     "name": name,
#                     "class": cls,
#                     "date": date,
#                     "time": time
#                 }

#     if not last_row:
#         return jsonify({"status": "fail"})

#     # Lấy ảnh mới nhất theo mã
#     images = sorted(
#         [img for img in os.listdir(IMAGE_DIR) if img.endswith(".jpg")],
#         reverse=True
#     )

#     return jsonify({
#         "status": "success",
#         "code": last_row["code"],
#         "name": last_row["name"],
#         "class": last_row["class"],
#         "image": images[0] if images else ""
#     })
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import face_recognition
import numpy as np
import base64
import cv2
import pickle
import os
from datetime import datetime

# ================== KHỞI TẠO APP ==================
app = Flask(__name__)
CORS(app)

# ================== CẤU HÌNH ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "attendance.csv")
IMAGE_DIR = os.path.join(BASE_DIR, "storage")

os.makedirs(IMAGE_DIR, exist_ok=True)

# ================== USER CỐ ĐỊNH ==================
USERS = {
    "1112": {
        "name": "XA ANH KHOA",
        "class": "11A1",
        "encoding_index": 0
    }
}

# ================== LOAD ENCODING ==================
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

# ================== SERVE IMAGE ==================
@app.route("/storage/<filename>")
def get_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

# ================== ĐIỂM DANH ==================
@app.route("/attendance", methods=["POST"])
def attendance():
    req = request.json
    code = req.get("code")
    img_data = req.get("image")

    if code not in USERS:
        return jsonify({"status": "fail", "message": "Mã không hợp lệ"})

    img_bytes = base64.b64decode(img_data.split(",")[1])
    np_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    if len(encodings) == 0:
        return jsonify({"status": "fail", "message": "Không phát hiện khuôn mặt"})

    user = USERS[code]
    known_encoding = data["encodings"][user["encoding_index"]]

    dist = face_recognition.face_distance([known_encoding], encodings[0])[0]
    accuracy = (1 - dist) * 100

    if dist > 0.5:
        return jsonify({"status": "fail", "accuracy": round(accuracy, 2)})

    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S") + ".jpg"
    img_path = os.path.join(IMAGE_DIR, filename)

    cv2.imwrite(img_path, np_img)

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{code},{user['name']},{user['class']},{now.date()},{now.strftime('%H:%M:%S')}\n")

    return jsonify({
        "status": "success",
        "name": user["name"],
        "class": user["class"],
        "accuracy": round(accuracy, 2)
    })

# ================== DANH SÁCH HÔM NAY ==================
@app.route("/today")
def today():
    result = []
    today = str(datetime.now().date())

    if not os.path.exists(DATA_FILE):
        return jsonify(result)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            code, name, cls, date, time = line.strip().split(",")
            if date == today:
                result.append({
                    "code": code,
                    "name": name,
                    "class": cls,
                    "date": date,
                    "time": time
                })

    return jsonify(result)

# ================== TRA CỨU THEO MÃ ==================
@app.route("/search/<code>")
def search(code):
    if not os.path.exists(DATA_FILE):
        return jsonify({"status": "fail"})

    last = None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            c, name, cls, date, time = line.strip().split(",")
            if c == code:
                last = {
                    "code": c,
                    "name": name,
                    "class": cls
                }

    if not last:
        return jsonify({"status": "fail"})

    images = sorted(os.listdir(IMAGE_DIR), reverse=True)

    return jsonify({
        "status": "success",
        "code": last["code"],
        "name": last["name"],
        "class": last["class"],
        "image": images[0] if images else ""
    })

# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)
