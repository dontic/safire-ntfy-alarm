# main.py

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import signal
import sys
import xml.etree.ElementTree as ET
import requests
import json
import logging
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Add basic logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)


# Configuration
NTFY_URL = os.getenv("NTFY_URL")
NTFY_TOKEN = os.getenv("NTFY_TOKEN")


class AlarmHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        log.info(f"Received POST request from {self.client_address}")

        log.info("Getting data from request...")

        # Log the headers
        log.info(f"Headers: {self.headers}")

        try:
            log.info("Parsing XML data...")

            # Read the data
            xml_data = self.rfile.read().decode("utf-8")
            log.info(f"Data received: {xml_data}")

            # Remove namespace to make parsing easier
            xml_data = xml_data.replace('xmlns="http://www.ipc.com/ver10"', "")
            root = ET.fromstring(xml_data)

            # Parse alarms
            alarms = {}
            for alarm in root.find("alarmStatusInfo"):
                alarms[alarm.tag] = alarm.text.lower() == "true"

            # Get device info
            device_info = {}
            for info in root.find("deviceInfo"):
                device_info[info.tag] = info.text.strip("[]")

            timestamp = root.find("dataTime").text.strip("[]")

            log.info(f"Alarms: {alarms}")

            # Alarms:
            # {
            #   'motionAlarm': True,
            #   'perimeterAlarm': False,
            #   'tripwireAlarm': False,
            #   'humanMotionAlarm': False,
            #   'vehicleMotionAlarm': False
            # }

            if any(alarms.values()):

                # Send notification to NTFY with all the alarm info
                log.info("Sending notification to NTFY...")

                def format_alarm_message(alarms, device_info, timestamp):
                    # Start with warning emoji and alarm header
                    message = ""

                    message += f"Time: {timestamp}\n"

                    # Add specific alarm details with bullet points
                    alarm_details = []
                    if alarms.get("humanMotionAlarm"):
                        alarm_details.append("\n- Human detected")
                    if alarms.get("vehicleMotionAlarm"):
                        alarm_details.append("\n- Vehicle detected")
                    if alarms.get("motionAlarm"):
                        alarm_details.append("\n- General motion detected")
                    if alarms.get("perimeterAlarm"):
                        alarm_details.append("\n- Perimeter breach")
                    if alarms.get("tripwireAlarm"):
                        alarm_details.append("\n- Tripwire crossed")

                    # Add all alarm details to message
                    message += "\n".join(alarm_details)

                    # Add device info
                    message += (
                        f"\n\nDevice name: {device_info.get('deviceName', 'Unknown')}"
                    )
                    message += f"\nDevice IP: {device_info.get('ipAddress', 'Unknown')}"

                    return message

                headers = {
                    "Authorization": f"Bearer {NTFY_TOKEN}",
                    "Title": "Security Alert",  # Add a title to the notification
                    "Priority": "5",  # High priority for alerts
                    "Tags": "warning,camera,security",  # Add relevant tags
                }

                # Format the message
                formatted_message = format_alarm_message(alarms, device_info, timestamp)

                # Send the notification
                response = requests.post(
                    NTFY_URL, headers=headers, data=formatted_message
                )

                if response.status_code != 200:
                    log.error(f"Error sending notification to NTFY: {response.text}")
                    raise Exception(
                        f"Error sending notification to NTFY: {response.text}"
                    )

                log.info("Notification sent to NTFY")

            else:
                log.info("No alarms detected")

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "success", "message": "Request processed"}
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(response).encode())


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nShutting down server...")
    sys.exit(0)


def run_http_server():
    PORT = 5000
    server = HTTPServer(("0.0.0.0", PORT), AlarmHandler)
    print(f"Server started on port {PORT}")
    server.serve_forever()

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal

    print(f"Server started on port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    run_http_server()
