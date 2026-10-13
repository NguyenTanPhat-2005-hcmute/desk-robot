# Desk Robot

**An ESP32 desk robot for study support, environmental monitoring, and local AI assistance.**

Desk Robot combines ESP32 hardware, a web dashboard, and a Python application into a companion for a study workspace. The robot measures environmental conditions, displays information and expressions on an OLED screen, moves its head and arms using servos, and supports Pomodoro study sessions. The dashboard provides sensor monitoring, robot controls, and study management tools, while the Python application adds conversational assistance through a local Ollama model.

This is an educational prototype for exploring IoT and AI integration. The repository includes firmware, a web interface, a desktop application, and hardware documentation.

<p align="center">
  <img src="docs/images/robot-prototype.png" alt="Desk Robot prototype with an OLED display, servos, and ESP32 hardware" width="360" />
</p>

<p align="center"><em>The physical prototype uses an OLED display for expressions and a layered frame to house the controller, wiring, and power supply.</em></p>

## Features

| Feature                  | Description                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| Environmental monitoring | Track temperature, humidity, light level, pressure, and estimated altitude                       |
| Robot interaction        | Display OLED expressions, control the head and both arms, and respond to touch input             |
| Focus sessions           | Run 25-minute study sessions with 5-minute breaks using the firmware's Pomodoro timer            |
| Web dashboard            | View device status, charts, activity logs, and robot controls through Firebase                   |
| Study management         | Use the web interface to organize schedules, notes, and study tasks                              |
| Local AI assistant       | Ask questions and analyze environmental or task context in the Python application through Ollama |
| Demo administration      | Manage accounts, roles, and robot access through the web interface                               |

## Web Dashboard

![Desk Robot dashboard showing environmental readings and system status](docs/images/dashboard.png)

The dashboard brings sensor readings, connection status, and robot information into a single view. Users can switch between workspace monitoring, controls, and activity logs, with separate pages for ChatBox, study tools, charts, and administration.

The **AI/MCP Analysis** panel displays environmental assessments and a reference comfort score. The dashboard can calculate these assessments using local rules when results from an external agent are unavailable. The `dashboard_local` label in the screenshot identifies this source. The comfort score is calculated by the software rather than measured directly by a sensor.

_The screenshot captures a single point in time; readings and status change with the data stored in Firebase._

## System Architecture

<p align="center">
  <img src="docs/images/system-architecture.png" alt="System architecture with sensors, ESP32 and actuators, Firebase, and the AI application and web dashboard" width="620" />
</p>

The system consists of four main blocks:

1. **Sensors:** the AHT20 measures temperature and humidity, the BMP280 measures pressure for altitude estimation, the BH1750 measures light level, and the TTP223 detects touch input.
2. **Processing and interaction:** the ESP32 reads sensors and manages the OLED, servos, and Pomodoro state. The firmware uploads environmental readings to Firebase approximately every 10 seconds.
3. **Data synchronization:** Firebase Realtime Database stores readings, robot state, and control requests. The dashboard subscribes to changes in these nodes to update its interface.
4. **Applications:** the web dashboard provides monitoring and controls. The Python application offers a chat interface, reads context from Firebase, and calls Ollama on the computer.

The firmware and dashboard use the following monitoring and control flows:

```text
Sensors → ESP32 → Firebase → Dashboard
Dashboard → Firebase/CommandRequest → ESP32 → OLED and servos
ESP32 → Firebase/CommandAck → Dashboard
```

The architecture diagram represents the overall integration design. The Python application currently runs through its desktop interface; connecting web ChatBox requests to Python requires an additional request-processing agent. See [Integration Status](#integration-status) for the current implementation scope.

### Data Layout

The firmware and dashboard organize data by robot:

```text
RobotDashboard/
└── Robots/
    └── <robotId>/
        ├── RobotInfo/
        ├── ThongSo/
        ├── ThietBi/
        │   ├── CommandRequest/
        │   └── CommandAck/
        ├── Dashboard/
        ├── Pomodoro/
        ├── ChatBox/
        └── MCP/
            └── EnvironmentAnalysis/
```

`CommandRequest` and `CommandAck` contain request identifiers and timestamps for tracking command receipt, execution, and latency. The firmware's `ROBOT_ID` must match the robot selected and authorized in the dashboard.

## Hardware

### Main Components

| Component                                       | Purpose                                                          |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| ESP32                                           | Central controller and Wi-Fi connectivity                        |
| SSD1306 OLED, 128 × 64                          | Expressions, environmental readings, clock, and Pomodoro display |
| AHT20 and BMP280                                | Temperature, humidity, and pressure measurements                 |
| BH1750                                          | Ambient light measurement                                        |
| TTP223                                          | Touch and hold input                                             |
| Three servos                                    | Head, left arm, and right arm movement                           |
| Power supply, switch, and LM2596 buck converter | Power delivery as shown in the wiring diagram                    |

### Circuit Schematic

![Circuit schematic showing the ESP32, OLED, sensors, three servos, and power supply](docs/images/circuit-schematic.png)

The schematic separates the processing, display, sensing, actuator, and power blocks. The OLED and environmental sensors share the I2C bus; the servos and touch sensor use dedicated signal pins.

### Wiring Diagram

![Wiring diagram connecting the ESP32 to the OLED, touch sensor, environmental sensors, three servos, and power supply](docs/images/wiring-diagram.png)

The wiring diagram illustrates the modules and their connections. The table below lists the pins currently declared in the firmware for reference during assembly or hardware changes.

| Signal              | Firmware GPIO |
| ------------------- | ------------- |
| I2C SDA             | 21            |
| I2C SCL             | 22            |
| TTP223 touch sensor | 4             |
| Head servo          | 18            |
| Left arm servo      | 16            |
| Right arm servo     | 17            |
| Buzzer              | 27            |
| Status LED          | 2             |

The buzzer and LED are additional outputs used by the firmware. The hardware images are reference diagrams; update the corresponding GPIO constants in the sketch when changing the wiring.

## Repository Structure

| File or directory        | Purpose                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------- |
| `robot_cua_tan_phat.ino` | ESP32 firmware for sensors, OLED, servos, Pomodoro, and Firebase                   |
| `AI_local.PY`            | Tkinter application for chat, context retrieval, task management, and UDP commands |
| `settings.py`            | Python configuration loaded from environment variables or `.env`                   |
| `index.html`             | Monitoring, control, and study management dashboard                                |
| `login.html`             | Demo registration, login, and EmailJS OTP interface                                |
| `emailjs-test.html`      | Email delivery configuration checks                                                |
| `assets/` and `images/`  | Web interface resources                                                            |
| `docs/images/`           | Product, dashboard, architecture, and hardware images used in this README          |
| `database.rules.json`    | Firebase Security Rules for the demo                                               |

## Configuration

| Local configuration file | Committed example   | Contents                                         |
| ------------------------ | ------------------- | ------------------------------------------------ |
| `.env`                   | `.env.example`      | ESP32 address, Firebase URL, and Ollama settings |
| `config.local.js`        | `config.example.js` | Firebase Web and EmailJS configuration           |
| `secrets.h`              | `secrets.example.h` | Wi-Fi and Firebase configuration for the ESP32   |

After cloning the repository on a new computer, create the configuration files using PowerShell:

```powershell
Copy-Item .env.example .env
Copy-Item config.example.js config.local.js
Copy-Item secrets.example.h secrets.h
```

Fill in the three files with your connection details. If they already exist, edit them directly to preserve your current configuration. Operating-system environment variables take precedence over values in `.env`.

The firmware's `ROBOT_ID` must match a robot authorized in the dashboard. `DATABASE_URL` in `secrets.h` must end with `/`.

## Running the Python App

Requirements: Python 3.10 or later with Tkinter, and Ollama running locally.

The example configuration uses `qwen2.5:3b`. AI inference runs on the computer; Firebase and EmailJS still require network access.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
```

In another terminal, activate the virtual environment and launch the application:

```powershell
python AI_local.PY
```

Set `OLLAMA_MODEL` in `.env` to use a different model. Check network connectivity, `ESP32_IP`, and `ESP32_PORT` before sending robot commands.

## Running the Dashboard

After completing `config.local.js`, start a local web server:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/login.html`. Use `emailjs-test.html` to check your EmailJS configuration. The OTP parameter names must match your email template.

When deploying the website, provide its web configuration through a separate deployment step. Keep `.env` and `secrets.h` out of publicly served directories.

## Flashing the Firmware

Open the sketch in Arduino IDE with an ESP32 board selected, place `secrets.h` beside the `.ino` file, and install these libraries:

- Adafruit GFX, Adafruit SSD1306, Adafruit AHTX0, and Adafruit BMP280
- BH1750
- ESP32Servo
- Firebase ESP Client

Check the GPIO assignments before flashing. Read the ESP32's IP address from the Serial Monitor.

## Integration Status

The components currently use different data layouts and control channels:

- **Firmware and dashboard:** use nodes under `RobotDashboard/Robots/<robotId>`. The firmware receives control requests through Firebase.
- **Python desktop app:** reads legacy nodes such as `ThongSo`, `Task`, and `ChatBox` at the database root by default. Align these paths when sharing data with the dashboard.
- **Web ChatBox:** writes questions to Firebase. `AI_local.PY` does not yet include a background loop that receives and processes these requests automatically.
- **UDP commands:** the Python app can send UDP commands, but the included firmware does not yet implement a corresponding UDP receiver.
- **AI/MCP:** the dashboard reads analysis results when available and supports local assessments. The repository does not include an MCP server or a background processing agent for this flow.

These integration tasks remain to be completed when connecting all components into a single system.

## Code Formatting

Install the Python formatting tools and Prettier. Prettier requires Node.js 18 or later:

```powershell
python -m pip install -r requirements-dev.txt
npm ci
```

Format and check the source:

```powershell
python -m black AI_local.PY settings.py
clang-format -i robot_cua_tan_phat.ino secrets.example.h
npm run format
python -m black --check AI_local.PY settings.py
npm run format:check
```

Formatting rules are defined in `pyproject.toml`, `.prettierrc.json`, `.clang-format`, and `.editorconfig`.
