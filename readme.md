# 🧠 Footfall Counter

A **Computer Vision-based People Counting System** that detects and counts the number of people entering and exiting a specified region in real time.
It leverages **Streamlit** for the user interface, **WebSocket** for communication, and **SORT / DeepSORT** for object tracking — all built with **Python**.

---

## 🚀 Features

* Detects and counts **entries** and **exits** in a specified region.
* Real-time video processing through **Streamlit** and **WebSocket**.
* Supports both **SORT** and **DeepSORT** tracking algorithms.
* User-friendly interface for defining boundaries dynamically.
* Customizable video input and region of interest selection.

---

## 🧩 Tech Stack

* **Language:** Python
* **Frameworks/Libraries:** Streamlit, OpenCV, NumPy
* **Tracking Algorithms:** SORT, DeepSORT
* **Communication:** WebSocket

---

## ⚙️ Installation and Setup

Follow these steps to set up and run the Footfall Counter:

### 1. Clone the Repository

```bash
git clone https://github.com/Tejas2124/footfall-counter.git
cd footfall-counter
```

### 2. Create a Virtual Environment

```bash
python -m venv fcount
```

### 3. Activate the Environment

* **Windows:**

  ```bash
  fcount\Scripts\activate
  ```
* **Linux/Mac:**

  ```bash
  source fcount/bin/activate
  ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Navigate to the App Directory

```bash
cd app
```

---

## ▶️ Running the Application

You’ll need **two terminals** (or split terminal views) to run the app.

### **Terminal 1 – Start the Video Server**

```bash
python video_server.py
```

### **Terminal 2 – Launch the Streamlit Interface**

```bash
streamlit run app.py
```

---

## 🎮 Usage

1. Open the Streamlit interface (it will launch automatically in your browser).
2. Choose how you want to capture the first frame using the **radio button options**.
3. Draw a **boundary** around the region of interest (entry/exit zone).
4. Start the counter and observe **real-time people entry and exit counts**.

---

## 🧠 Algorithms Used

* **SORT (Simple Online and Realtime Tracking)** — A lightweight tracker for fast applications.
* **DeepSORT** — Extends SORT with appearance features using deep learning, providing more robust multi-object tracking.

---

## 🧰 Troubleshooting

* Ensure your camera or video source is accessible.
* Use the correct Python version (recommended: **Python 3.10+**).
* If you encounter dependency errors, reinstall using:

  ```bash
  pip install --upgrade -r requirements.txt
  ```
* For performance improvement, GPU usage can be configured in tracker settings if supported.

---

## 👨‍💻 Author

**Tejas Raval**  
📧 [Mail](2x3osjs@gmail.com)  
💼 LinkedIn: [Tejas Raval](https://www.linkedin.com/in/tejas-raval-2a5103234/])

---

## Video Explaination

* ### **In hindi**   
[![Hindi Video](https://i9.ytimg.com/vi/HEaOSsQCAnI/mq2.jpg?sqp=CJipr8gG&rs=AOn4CLDk1Szwq10ZKPvbUq33ZzTT3d0V8Q)](https://youtu.be/UryzXhXC6U4)
* ### **In English**   
[![English Video](https://i9.ytimg.com/vi/HEaOSsQCAnI/mq2.jpg?sqp=CJipr8gG&rs=AOn4CLDk1Szwq10ZKPvbUq33ZzTT3d0V8Q)](https://youtu.be/HEaOSsQCAnI)
