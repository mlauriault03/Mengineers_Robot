from flask import Flask, jsonify
from codrone_edu.drone import Drone

app = Flask(__name__)
drone = Drone()
drone.pair()

@app.route("/takeoff", methods=["POST"])
def takeoff():
    drone.takeoff()
    return jsonify({"status": "taking off"})

@app.route("/land", methods=["POST"])
def land():
    drone.land()
    return jsonify({"status": "landing"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)