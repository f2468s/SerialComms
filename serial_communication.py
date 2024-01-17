from flask import Flask, render_template, request
import serial.tools.list_ports
import threading

app = Flask(__name__)
ser = None
serial_data = ""
available_ports = {}


def get_available_ports():
    return [port.device for port in serial.tools.list_ports.comports()]


@app.route("/")
def index():
    global available_ports
    return render_template("index.html", serial_data=serial_data, available_ports=available_ports)


def read_serial():
    global ser, serial_data
    while True:
        if ser:
            serial_data = ser.readline().decode("utf-8").strip()


@app.route("/open_serial", methods=["POST"])
def open_serial():
    global ser
    if not ser or not ser.is_open:
        try:
            port = request.form.get("port")
            baudrate = request.form.get("baudrate")
            ser = serial.Serial(port, baudrate)
            threading.Thread(target=read_serial).start()
            return "Serial port opened successfully."
        except serial.SerialException as e:
            return f"Error opening serial port: {str(e)}"
    else:
        return "Serial port is already open."


@app.route("/send_data/<int:window_number>", methods=["POST"])
def send_data(window_number):
    global ser
    label = request.form.get("label" + str(window_number))
    data_type = request.form.get("data_type" + str(window_number))
    data = request.form.get("data" + str(window_number))

    try:
        if data_type == "ascii":
            ser.write(data.encode("utf-8"))
        elif data_type == "hex":
            hex_bytes = bytes.fromhex(data)
            ser.write(hex_bytes)

        return f"Data sent successfully from {label}."
    except serial.SerialException as e:
        return f"Error sending data: {str(e)}"


@app.route("/close_serial")
def close_serial():
    global ser
    if ser and ser.is_open:
        ser.close()
        return "Serial port closed."
    else:
        return "Serial port is not open."


if __name__ == "__main__":
    available_ports = get_available_ports()
    app.run(debug=True)
