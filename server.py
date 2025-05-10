from flask import Flask, request, jsonify, render_template_string
from multi_sensor_distance import setup_sensors, monitor_sensors
from multi_sensor_line import setup as setup_line, read_sensors as monitor_line
from database import create_database, fetch_combined_data, insert_line_sensors, insert_distance_sensors, insert_controls
from datetime import datetime
from collections import OrderedDict
import psutil
import subprocess
import threading
import json
import os
import multiprocessing
import time
import socket
import sqlite3
import asyncio



DATABASE_PATH = "robot_data.db"
app = Flask(__name__)

current_control_system = "Manual control"  
current_action = "stop"            
current_speed = 50
logging_active = True

process_targets = {
    "action_update_process": lambda: update_current_action(),
    "sensor_update_process": lambda: update_shared_data(),
    "color_sensor_process": lambda: update_color_sensor_data(),
    "monitor_process": lambda: monitor_distance_sensors(),
    "logging_process": lambda: log_data()
}

control_data_manager = multiprocessing.Manager()
shared_control_data = control_data_manager.dict()
sensor_data_manager = multiprocessing.Manager()
shared_sensor_data = sensor_data_manager.dict()
color_sensor_data_manager = multiprocessing.Manager()
shared_color_sensor_data = color_sensor_data_manager.dict()

active_process = None
lock = threading.Lock()
control_lock = threading.Lock()

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Robot Control</title>
            <script>
                let currentSpeed = 50; // Domyďż˝lna wartoďż˝ďż˝ prďż˝dkoďż˝ci
                let lastSpeed = 50;
                let pendingSpeed = 50; // Tymczasowa wartość prędkości, zapisywana dopiero po naciśnięciu przycisku
                let speedLocked = false; // Flaga blokady suwaka
                
                async function updateSpeed(value) {
                    const savedSystem = localStorage.getItem("currentSystem") || "Manual control";
                    
                    if (savedSystem !== "Manual control") {
                        return;
                    }

                    pendingSpeed = parseInt(value, 10); // Ustawiamy nową wartość lokalnie

                    // Natychmiastowa aktualizacja wyświetlanej wartości prędkości
                    const speedSlider = document.getElementById("speed-slider");
                    const speedValue = document.getElementById("speed-value");

                    if (speedSlider && speedValue) {
                        speedSlider.value = pendingSpeed;
                        speedValue.innerText = `${pendingSpeed}%`;
                    }
                }


                async function sendRequest(scriptName) {
                    // Mapa przypisująca nazwy skryptów do czytelnych nazw
                    const scriptNames = {
                        "main_16": "Avoiding obstacles 1",
                        "main_64": "Avoiding obstacles 2",
                        "main_line": "Following the line",
                        "main_line_64": "Combined mode",
                        "manual_control": "Manual control",
                        "show_ride": "Driving demonstration"
                    };

                    // Pobranie czytelnej nazwy na podstawie scriptName
                    const displayName = scriptNames[scriptName] || scriptName; // Jeśli brak mapowania, używa oryginalnej nazwy

                    localStorage.setItem("currentSystem", displayName);

                    // Aktualizacja pola Current System na czytelną nazwę
                    document.getElementById("control-system").innerText = "Current System: " + displayName;

                    try {
                        const response = await fetch('/run-script', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ script_name: scriptName })
                        });

                        const data = await response.json();

                        if (data.error) {
                            document.getElementById("control-system").innerText = "Błąd uruchamiania!";
                        } else {
                            document.getElementById("control-system").innerText = `Current System: ${displayName}`;
                        }
                    } catch (error) {
                        console.error("Error:", error);
                        document.getElementById("control-system").innerText = "Błąd!";
                    }
                }
                
               async function restoreSystem() {
                    try {
                        const savedSystem = localStorage.getItem("currentSystem") || "Manual control";
                        const systemElement = document.getElementById("control-system");
                        const speedSlider = document.getElementById("speed-slider");
                        const speedValue = document.getElementById("speed-value");

                        if (systemElement) {
                            systemElement.innerText = `Current System: ${savedSystem}`;
                        }

                        const lockedModes = ["Avoiding obstacles 1", "Avoiding obstacles 2", "Following the line", "Combined mode", "Driving demonstration"];
                        speedLocked = lockedModes.includes(savedSystem);

                        if (speedSlider) {
                            speedSlider.disabled = speedLocked;
                            speedSlider.style.backgroundColor = speedLocked ? "#d3d3d3" : ""; 
                        }
                    } catch (error) {
                        console.error("⚠ Błąd przywracania systemu:", error);
                    }
                }

                async function updateCurrentAction() {
                    try {
                        const response = await fetch('/current-action');
                        const data = await response.json();

                        const statusElement = document.getElementById("status");
                        if (statusElement.innerText !== `Current Action: ${data.action}`) {
                            statusElement.innerText = `Current Action: ${data.action}`;
                        }

                        // Nie nadpisuj prędkości, jeśli użytkownik zmienił suwak ręcznie
                        if (data.action !== "stop" && data.speed !== undefined && data.speed !== pendingSpeed) {
                            lastSpeed = data.speed;
                            if (!document.activeElement || document.activeElement.id !== "speed-slider") {
                                const speedSlider = document.getElementById("speed-slider");
                                const speedValue = document.getElementById("speed-value");
                                speedSlider.value = lastSpeed;
                                speedValue.innerText = `${lastSpeed}%`;
                            }
                        }
                    } catch (error) {
                        console.error("Error fetching current action:", error);
                    }
                }

                async function updateColorSensors() {
                    try {
                        const response = await fetch('/color-sensors');
                        const data = await response.json();

                        // Sprawdź, czy element #color-sensors istnieje przed jego aktualizacją
                        const colorElement = document.getElementById("color-sensors");
                        if (colorElement) {
                            const values = `${data.outer_left} ${data.middle_left} ${data.middle_right} ${data.outer_right}`;
                            colorElement.innerText = values;
                        } else {
                            console.error("Element #color-sensors nie istnieje!");
                        }
                    } catch (error) {
                        console.error("Error fetching color sensor data:", error);
                    }
                }
                
                // Funkcja do wysyďż˝ania komend AJAX-em
                async function sendCommand(action) {
                    const savedSystem = localStorage.getItem("currentSystem") || "Manual control";
                    
                    if (savedSystem !== "Manual control") {
                        return;
                    }

                    lastSpeed = pendingSpeed; // Zapisujemy nową prędkość dopiero w momencie wysłania komendy

                    try {
                        const response = await fetch('/control', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ action: action, speed: lastSpeed })
                        });

                        const data = await response.json();
                        document.getElementById("status").innerText = "Current Action: " + data.action;

                    } catch (error) {
                        console.error("⚠ Błąd wysyłania komendy:", error);
                    }
                }

                // Funkcja do aktualizacji odczytďż˝w czujnikďż˝w
                async function updateSensors() {
                    fetch('/sensors', {
                        method: 'GET'
                    }).then(response => response.json())
                      .then(data => {
                          for (let i = 0; i < 6; i++) {
                              const sensorElement = document.getElementById("sensor" + i);
                              const distance = parseFloat(data.sensors[i]).toFixed(1);
                              sensorElement.innerText = distance + " cm";

                              // Zmiana koloru na podstawie zakresu odlegďż˝oďż˝ci
                              if (distance < 20) {
                                  sensorElement.style.backgroundColor = "red";
                              } else if (distance < 50) {
                                  sensorElement.style.backgroundColor = "yellow";
                              } else {
                                  sensorElement.style.backgroundColor = "green";
                              }
                          }
                      })
                      .catch(error => {
                          console.error("Error:", error);
                      });

                    fetch('/color-sensors', {
                        method: 'GET'
                    }).then(response => response.json())
                      .then(data => {
                          const values = `${data.outer_left} ${data.middle_left} ${data.middle_right} ${data.outer_right}`;
                          const colorElement = document.getElementById("color-sensors");
                          if (colorElement) {
                              colorElement.innerText = values;
                          } else {
                              console.error("Element #color-sensors nie istnieje!");
                          }
                      })
                      .catch(error => console.error("Error fetching color sensors:", error));
                }

                // Funkcja do zmiany systemu sterujďż˝cego
                async function changeControlSystem(system) {
                    fetch('/control-system', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ system: system })
                    }).then(response => response.json())
                      .then(data => {
                          document.getElementById("control-system").innerText = "Current System: " + data.system;
                      })
                      .catch(error => {
                          console.error("Error:", error);
                      });
                }

                async function clearDatabase() {
                    try {
                        const response = await fetch('/clear-database', {
                            method: 'POST'
                        });

                        const data = await response.json();
                        alert(data.message);
                    } catch (error) {
                        console.error("Błąd:", error);
                    }
                }

                function startAutoUpdate() {
                    updateColorSensors();
                    updateSensors();
                    updateCurrentAction();
                    setInterval(updateColorSensors, 1000);
                    setInterval(updateSensors, 1000);
                    setInterval(updateCurrentAction, 1000);
                }

                // Przywróć wartość po załadowaniu strony
                window.onload = restoreSystem;
                document.addEventListener("DOMContentLoaded", () => {
                    restoreSystem();
                    updateCurrentAction();
                });

                document.addEventListener("visibilitychange", () => {
                    if (!document.hidden) {
                        restoreSystem();
                        updateCurrentAction();
                    }
                });
                document.addEventListener("DOMContentLoaded", updateCurrentAction);

                document.addEventListener("DOMContentLoaded", startAutoUpdate);
            </script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    flex-direction: row;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin: 0;
                    padding: 0;
                }
                h1 {
                    color: #4CAF50;
                    text-align: center;
                }
                .main-content {
                    flex: 3;
                    text-align: center;
                    padding: 20px;
                }
                .sidebar {
                    flex: 1;
                    text-align: center;
                    border-left: 2px solid #ddd;
                    padding: 20px;
                    box-shadow: -2px 0px 10px rgba(0, 0, 0, 0.1);
                }
                .circle {
                    position: relative;
                    width: 300px;
                    height: 300px;
                    border: 2px solid black;
                    border-radius: 50%;
                    margin: 40px auto;
                    background-color: #f9f9f9;
                }
                .sensor {
                    position: absolute;
                    font-size: 16px;
                    background-color: #fff;
                    padding: 5px;
                    border-radius: 5px;
                    text-align: center;
                    min-width: 40px;
                }
                #sensor0 { top: -10px; left: 50%; transform: translate(-50%, -50%); }
                #sensor1 { top: 25%; left: 90%; transform: translate(-50%, -50%); }
                #sensor2 { top: 75%; left: 90%; transform: translate(-50%, -50%); }
                #sensor3 { top: 100%; left: 50%; transform: translate(-50%, -50%); }
                #sensor4 { top: 75%; left: 10%; transform: translate(-50%, -50%); }
                #sensor5 { top: 25%; left: 10%; transform: translate(-50%, -50%); }
                .color-sensor {
                    margin-top: 20px;
                    padding: 10px;
                    font-size: 24px;
                    font-weight: bold;
                    border: 2px solid black;
                    border-radius: 10px;
                    display: inline-block;
                    background-color: #eaeaea;
                }
                .button {
                    width: 60px;
                    height: 60px;
                    font-size: 20px;
                    border: none;
                    border-radius: 50%;
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    transition: background-color 0.3s;
                    margin: 10px 0;
                }
                .button:active {
                    box-shadow: none;
                    transform: translateY(2px);
                }
                .control-system-buttons button {
                    margin: 5px;
                    padding: 10px 20px;
                    font-size: 16px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                .control-system-buttons button:hover {
                    background-color: #f1f1f1;
                }
                .slider { 
                    width: 50%; 
                }
                .speed-container { 
                    text-align: center; margin: 20px 0; 
                }
                #status {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="main-content">
                <h1>Robot Control</h1>

                <!-- Wyďż˝wietlanie obecnego systemu sterowania -->
                <p id="control-system">Current System: Manual control</p>
                <div class="control-system-buttons">
                    <button onclick="sendRequest('main_16')">Avoiding obstacles 1</button>
                    <button onclick="sendRequest('main_64')">Avoiding obstacles 2</button>
                    <button onclick="sendRequest('main_line')">Following the line</button>
                    <button onclick="sendRequest('main_line_64')">Combined mode</button>
                    <button onclick="sendRequest('manual_control')">Manual control</button>
                    <button onclick="sendRequest('show_ride')">Driving demonstration</button>
                    <button onclick="window.location.href='/logs'">Saved data</button>
                    <button onclick="clearDatabase()">Clear data</button>
                </div>

                <div id="color-sensors" class="color-sensor">N/A</div>

                <!-- Odczyty czujnikďż˝w w ukďż˝adzie koďż˝owym -->
                <div class="circle">
                    <div id="sensor0" class="sensor">0 cm</div>
                    <div id="sensor1" class="sensor">0 cm</div>
                    <div id="sensor2" class="sensor">0 cm</div>
                    <div id="sensor3" class="sensor">0 cm</div>
                    <div id="sensor4" class="sensor">0 cm</div>
                    <div id="sensor5" class="sensor">0 cm</div>
                </div>

                <!-- Aktualny stan -->
                <p id="status">Current Action: stop</p>
            </div>
            <div class="sidebar">
                <h2>Manual Control</h2>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-left-forward')">↖</button>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-forward')">⬆</button>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-right-forward')">↗</button><br>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-left')">⬅</button>
                <button class="button" style="background-color: lightcoral;" onclick="sendCommand('stop')">⏹</button>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-right')">➡</button><br>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-left-backward')">↙</button>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-backward')">⬇</button>
                <button class="button" style="background-color: lightblue;" onclick="sendCommand('move-right-backward')">↘</button><br>
                <button class="button" style="background-color: lightgreen;" onclick="sendCommand('move-turn-left')">⟲</button>
                <button class="button" style="background-color: lightgreen;" onclick="sendCommand('move-turn-right')">⟳</button><br>
                <div class="speed-container">
                    <label for="speed-slider">Speed:</label>
                    <input id="speed-slider" type="range" min="0" max="100" value="50" class="slider" oninput="updateSpeed(this.value)">
                    <span id="speed-value">50%</span>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/logs')
def logs():
    data = fetch_combined_data()
    columns = ["Id", "Timestamp", "Action", "Speed",
               "Left Front", "Front", "Right Front", "Right Back", "Back", "Left Back",
               "Outer Left", "Middle Left", "Middle Right", "Outer Right",]
    return render_template_string(get_logs_template(), table_data=data, columns=columns, table_type="combined")


@app.route('/logs/line-sensors')
def logs_line_sensors():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM line_sensors ORDER BY id DESC")
    data = cursor.fetchall()
    columns = ["Id", "Timestamp", "Outer Left", "Middle Left", "Middle Right", "Outer Right"]
    conn.close()
    return render_template_string(get_logs_template(), table_data=data, columns=columns, table_type="line_sensors")


@app.route('/logs/distance-sensors')
def logs_distance_sensors():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM distance_sensors ORDER BY id DESC")
    data = cursor.fetchall()
    columns = ["Id", "Timestamp", "Left Front", "Front", "Right Front", "Right Back", "Back", "Left Back"]
    conn.close()
    return render_template_string(get_logs_template(), table_data=data, columns=columns, table_type="distance_sensors")


@app.route('/logs/controls')
def logs_controls():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM controls ORDER BY id DESC")
    data = cursor.fetchall()
    columns = ["Id", "Timestamp", "Action", "Speed"]
    conn.close()
    return render_template_string(get_logs_template(), table_data=data, columns=columns, table_type="controls")

@app.route("/logs/line-sensors/data")
def line_sensors_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT `outer_left`, `middle_left`, `middle_right`, `outer_right` FROM line_sensors")
    data = cursor.fetchall()
    conn.close()

    labels = ["Outer Left", "Middle Left", "Middle Right", "Outer Right"]
    counts = [0] * len(labels)

    for row in data:
        for i, value in enumerate(row):
            counts[i] += value

    ordered_data = list(zip(labels, counts))
    
    return jsonify(ordered_data)


@app.route("/logs/controls/data")
def controls_data():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM controls")
        all_rows = cursor.fetchall()
        print("All rows in controls table:", all_rows)

        cursor.execute("SELECT `action` FROM controls WHERE `action` != 'stop'")
        data = cursor.fetchall()
        conn.close()

        counts = {}
        for row in data:
            action = row[0]
            counts[action] = counts.get(action, 0) + 1

        print("Action counts:", counts)

        return jsonify(counts)

    except Exception as e:
        print(f"Error in controls_data: {e}")
        return jsonify({"error": str(e)})


@app.route("/logs/distance-sensors/data")
def distance_sensors_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT `left_front_distance`, `front_distance`, `right_front_distance`,
               `right_back_distance`, `back_distance`, `left_back_distance` 
        FROM distance_sensors
    """)  
    data = cursor.fetchall()
    conn.close()

    labels = ["Left Front", "Front", "Right Front", "Right Back", "Back", "Left Back"]
    
    if data:
        averages = OrderedDict([
            (labels[i], round(sum(row[i] for row in data) / len(data), 2)) 
            for i in range(len(labels))
        ])
    else:
        averages = OrderedDict([(label, 0) for label in labels])

    return jsonify(list(averages.items()))

def get_logs_template():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logs - {{ table_type }}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }
            .nav {
                text-align: center;
                margin: 20px 0;
            }
            .nav a {
                text-decoration: none;
                color: #007BFF;
                margin: 0 15px;
                font-size: 16px;
            }
            .nav a:hover {
                text-decoration: underline;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                table-layout: auto;
            }
            th, td {
                padding: 8px 12px;
                text-align: center;
                border: 1px solid #ddd;
                word-wrap: break-word;
            }
            th {
                background-color: #f4f4f4;
            }
            .chart-container {
                width: 80%;
                margin: 20px auto;
            }
            .chart {
                margin: 20px 0;
                padding: 10px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            #controls-chart {
                width: 50%; /* Adjust width as a percentage */
                height: 50%; /* Adjust height as a percentage */
                display: block; /* Ensure the canvas behaves like a block element */
                margin: 0 auto; /* Center the canvas horizontally */
            }
        </style>
    </head>
    <body>
        <h1>{{ table_type.replace('_', ' ').title() }}</h1>
        <div class="nav">
            <a href="/">Back to the main page</a> |
            <a href="/logs">Combined Data</a> |
            <a href="/logs/line-sensors">Line Sensors</a> |
            <a href="/logs/distance-sensors">Distance Sensors</a> |
            <a href="/logs/controls">Controls</a>
        </div>

        {% if table_type != "combined" %}
        <div class="chart-container" style="width: 70%; margin: 20px auto;">
            <h2>Chart for {{ table_type.replace('_', ' ').title() }}</h2>
            <canvas id="chart" class="chart"></canvas>
        </div>
        {% endif %}

        <table>
            <thead>
                <tr>
                    {% for column in columns %}
                    <th>{{ column }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in table_data %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <script>
            const tableType = "{{ table_type }}";
            const chartCtx = document.getElementById('chart')?.getContext('2d');

            if (tableType === "line_sensors") {
                fetch('/logs/line-sensors/data')
                    .then(response => response.json())
                    .then(data => {
                        const labels = data.map(item => item[0]);
                        const values = data.map(item => item[1]);

                        new Chart(chartCtx, {
                            type: 'bar',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Zliczona wartość 1',
                                    data: values,
                                    backgroundColor: ['red', 'blue', 'green', 'purple'],
                                }],
                            },
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: { display: false },
                                },
                                scales: {
                                    x: { title: { display: true, text: 'Sensors' } },
                                    y: { title: { display: true, text: 'Number of line detections' } },
                                },
                            },
                        });
                    })
                    .catch(error => console.error("Error fetching line sensors data:", error));
            } else if (tableType === "controls") {
                fetch("/logs/controls/data")
                    .then(response => response.json())
                    .then(data => {
                        // Remove the default chart canvas element
                        const chartContainer = document.querySelector(".chart-container");
                        const existingChart = document.getElementById("chart");
                        if (existingChart) {
                            chartContainer.removeChild(existingChart);
                        }

                        // Create a new canvas specifically for the controls chart
                        const newCanvas = document.createElement("canvas");
                        newCanvas.id = "controls-chart";
                        newCanvas.style.width = "50%"; // Set explicit width
                        newCanvas.height = 600; // Set explicit height
                        chartContainer.appendChild(newCanvas);

                        // Create the pie chart with fixed size
                        new Chart(newCanvas.getContext("2d"), {
                            type: "pie",
                            data: {
                                labels: Object.keys(data),
                                datasets: [{
                                    data: Object.values(data),
                                    backgroundColor: [
                                        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"
                                    ],
                                }],
                            },
                            options: {
                                responsive: false, // Disable responsiveness to respect canvas size
                                plugins: {
                                    legend: {
                                        display: true,
                                        position: "bottom", // Place legend at the bottom
                                        labels: {
                                            boxWidth: 15,
                                            font: { size: 12 },
                                        },
                                    },
                                },
                                layout: {
                                    padding: {
                                        top: 10,
                                        bottom: 10,
                                    },
                                },
                            },
                        });
                    })
                    .catch(error => console.error("Error fetching controls data:", error));
            } else if (tableType === "distance_sensors") {
                fetch('/logs/distance-sensors/data')
                    .then(response => response.json())
                    .then(data => {
                        const labels = data.map(item => item[0]);
                        const values = data.map(item => item[1]); 

                        new Chart(chartCtx, {
                            type: 'bar',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Average distance',
                                    data: values,
                                    backgroundColor: 'rgba(0, 123, 255, 0.7)',
                                }],
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    x: { title: { display: true, text: 'Sensors' } },
                                    y: { title: { display: true, text: 'Distance (cm)' } },
                                },
                            },
                        });
                    })
                    .catch(error => console.error("Error fetching distance sensors data:", error));
            }
        </script>
    </body>
    </html>
    '''

def start_process(script_name):
    global active_process

    stop_active_process()

    try:
        active_process = subprocess.Popen(
            ['nohup', 'python3', f'{script_name}.py', '&'],
            stderr=subprocess.STDOUT,
            text=True
        )
        return True
    except Exception as e:
        return False



def update_current_action():
    global current_action
    last_action = None
    while True:
        try:
            if os.path.exists('controls.json'):
                with open('controls.json', 'r') as f:
                    data = json.load(f)
                    new_action = data.get("action", "stop")
                    if new_action != last_action:
                        current_action = new_action
                        last_action = new_action
            else:
                if last_action != "stop":
                    current_action = "stop"
                    last_action = "stop"
        except Exception as e:
            print(f"Error while reading controls.json: {e}")
        time.sleep(0.1)

def read_control_data():
    if os.path.exists('controls.json'):
        try:
            with open('controls.json', 'r') as f:
                data = f.read().strip()
                if not data:
                    return {"action": "stop", "speed": 50}
                parsed_data = json.loads(data)

                parsed_data["speed"] = int(parsed_data.get("speed", 50))

                return parsed_data
        except json.JSONDecodeError:
            return {"action": "stop", "speed": 50}
    return {"action": "stop", "speed": 50}

def update_shared_control_data():
    while True:
        try:
            control_data = read_control_data()
            for key, value in control_data.items():
                shared_control_data[key] = value
            time.sleep(0.1)
        except Exception as e:
            print(f"Error updating control data: {e}")

def update_color_sensor_data():
    while True:
        try:
            if os.path.exists('sensor_color.json'):
                with open('sensor_color.json', 'r') as file:
                    data = json.load(file)
                    for key, value in data.items():
                        shared_color_sensor_data[key] = value
            else:
                print("File sensor_color.json does not exist.")
        except Exception as e:
            print(f"Error while reading sensor_color.json: {e}")
        time.sleep(0.5)

def stop_active_process():
    global active_process
    with lock:
        if active_process and active_process.poll() is None:
            active_process.terminate()
            try:
                active_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                active_process.kill()
            active_process = None

def read_sensors():
    try:
        if os.path.exists('sensors.json') and os.path.getsize('sensors.json') > 0:
            with open('sensors.json', 'r') as f:
                return json.load(f)
        else:
            return {}
    except json.JSONDecodeError as e:
        return {"F": 200, "RF": 200, "RB": 200, "B": 200, "LF": 200, "LB": 200}


def log_data():
    create_database()

    global logging_active
    while logging_active:
        try:
            controls = read_control_data()
            distances = read_sensors()

            line_sensors = dict(shared_color_sensor_data)

            insert_controls(controls)
            insert_distance_sensors(distances)
            insert_line_sensors(line_sensors)

            print(f"[{datetime.now()}] Data logged: Controls: {controls}, Distances: {distances}, Line Sensors: {line_sensors}")

        except Exception as e:
            print(f"Error logging data: {e}")

        time.sleep(1)

def monitor_controls():
    global shared_control_data
    last_control_data = {}
    
    while True:
        try:
            control_data = read_control_data()
            if control_data != last_control_data:
                with lock:
                    shared_control_data.update(control_data)
                    last_control_data = control_data.copy()

                    update_control_data(
                        action=control_data.get("action"), 
                        speed=control_data.get("speed")
                    )
        except Exception as e:
            print(f"Error while monitoring controls.json: {e}")
        time.sleep(0.1)


def monitor_distance_sensors():
    setup_sensors()
    while True:
        try:
            monitor_sensors()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error while monitoring distance sensors: {e}")

def monitor_line_sensors():
    setup_line()
    while True:
        try:
            monitor_line()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error while monitoring line sensors: {e}")

def get_color_sensors2():
    try:
        if os.path.exists('sensor_color.json'):
            with open('sensor_color.json', 'r') as f:
                return json.load(f)
        return {"ol": 0, "ml": 0, "mr": 0, "or": 0}
    except Exception as e:
        print(f"Error reading sensor_color.json: {e}")
        return {"ol": 0, "ml": 0, "mr": 0, "or": 0}
    

def clear_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM line_sensors")
    cursor.execute("DELETE FROM distance_sensors")
    cursor.execute("DELETE FROM controls")

    conn.commit()
    conn.close()

@app.route('/current-system', methods=['GET'])
def get_current_system():
    return jsonify({"system": current_control_system})

@app.route('/clear-database', methods=['POST'])
def clear_database_endpoint():
    try:
        clear_database()
        return jsonify({"message": "Baza danych została wyczyszczona."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run-script', methods=['POST'])
def run_script():
    data = request.json
    script_name = data.get('script_name')

    if not script_name:
        return jsonify({"error": "Brak nazwy skryptu"}), 400

    success = start_process(script_name)
    if success:
        return jsonify({"message": f"Skrypt {script_name}.py został uruchomiony"}), 200
    else:
        return jsonify({"error": "Nie udało się uruchomić skryptu"}), 500

def check_if_process_running(script_name):
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        if script_name in " ".join(proc.info['cmdline']):
            return True
    return False


def send_command(command):
    HOST = '127.0.0.1'
    PORT = 65432

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode('utf-8'))
            print(f"Command sent: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")



@app.route('/current-action', methods=['GET'])
def get_current_action():
    try:
        return jsonify({
            "action": shared_control_data.get("action", "stop"),
            "speed": shared_control_data.get("speed", 50)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/control', methods=['POST'])
def control():
    global current_action
    action = request.json.get('action')
    speed = request.json.get('speed', current_speed)
    if action:
        current_action = action
        send_command(f"{current_action}:{speed}")
        return jsonify({"action": current_action, "speed": speed})
    else:
        return jsonify({"error": "Invalid action"}), 400


@app.route('/control', methods=['GET'])
def controls():
    try:
        control_data = read_control_data()
        return jsonify(control_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sensors', methods=['GET'])
def sensors():
    sensor_data = dict(shared_sensor_data)
    ordered_sensors = [sensor_data.get("F"), sensor_data.get("RF"), sensor_data.get("RB"), sensor_data.get("B"), sensor_data.get("LB"), sensor_data.get("LF")]
    return jsonify({"sensors": ordered_sensors})

@app.route('/color-sensors', methods=['GET'])
def get_color_sensors():
    try:
        return jsonify({
            "outer_left": shared_color_sensor_data.get("ol", 0),
            "middle_left": shared_color_sensor_data.get("ml", 0),
            "middle_right": shared_color_sensor_data.get("mr", 0),
            "outer_right": shared_color_sensor_data.get("or", 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_sensor_data():
    if os.path.exists('sensors.json'):
        with open('sensors.json', 'r') as f:
            return json.load(f)
    return {"F": 200, "RF": 200, "RB": 200, "B": 200, "LF": 200, "LB": 200}

def update_shared_data():
    while True:
        try:
            sensor_data = get_sensor_data()
            for name, distance in sensor_data.items():
                shared_sensor_data[name] = distance
            time.sleep(0.3)
        except Exception as e:
            print(f"Sensor data update error: {e}")

def update_control_data(action=None, speed=None):
    with control_lock:
        try:
            control_data = read_control_data()

            if action is not None:
                control_data["action"] = action

            if speed is not None:
                control_data["speed"] = int(speed)

            with open("controls.json", "w") as f:
                json.dump(control_data, f)
            
        except Exception as e:
            print(f"Error writing to controls.json: {e}")

@app.route('/set-speed', methods=['POST'])
def set_speed():
    speed = request.json.get('speed')
    if speed is not None:
        update_control_data(speed=int(speed))
        return jsonify({"message": f"Speed set to {speed}%"}), 200
    return jsonify({"error": "Invalid speed value"}), 400


@app.route('/control-system', methods=['POST'])
def control_system():
    global current_control_system
    system = request.json.get('system')
    if system:
        current_control_system = system
        return jsonify({"system": current_control_system})
    return jsonify({"error": "Invalid system value"}), 400

def check_process_running(process):
    return process.is_alive() if process else False

async def async_monitor_sensors():
    from multi_sensor_distance import setup_sensors, monitor_sensors

    setup_sensors()

    while True:
        try:
            await monitor_sensors()
        except Exception as e:
            print(f"Distance sensor monitoring error: {e}")
        await asyncio.sleep(0.1)

async def async_monitor_line_sensors():
    from multi_sensor_line import setup as setup_line, read_sensors

    setup_line()

    while True:
        try:
            await read_sensors()
        except Exception as e:
            print(f"Line sensor monitoring error: {e}")
        await asyncio.sleep(0.1)

def run_async_task(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func())

def start_monitoring_processes():
    process_sensors = multiprocessing.Process(target=run_async_task, args=(async_monitor_sensors,))
    process_line = multiprocessing.Process(target=run_async_task, args=(async_monitor_line_sensors,))

    process_sensors.start()
    process_line.start()

    return [process_sensors, process_line]

async def main():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, app.run, '0.0.0.0', 5000, False)

if __name__ == '__main__':
    print("Starting processes...")
    action_update_process = multiprocessing.Process(target=update_current_action, daemon=True)
    sensor_update_process = multiprocessing.Process(target=update_shared_data, daemon=True)
    color_sensor_process = multiprocessing.Process(target=update_color_sensor_data, daemon=True)
    monitor_process = multiprocessing.Process(target=monitor_controls, daemon=True)
    logging_process = multiprocessing.Process(target=log_data, daemon=True)

    action_update_process.start()
    sensor_update_process.start()
    color_sensor_process.start()
    monitor_process.start()
    logging_process.start()

    sensor_processes = start_monitoring_processes()

    try:
        print("Starting the server Flask...")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("Stopping the server...")
    finally:
        for proc in [action_update_process, sensor_update_process, color_sensor_process, monitor_process, logging_process] + sensor_processes:
            proc.terminate()
            proc.join()

        print("All processes stopped")