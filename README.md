## 🎓 Campus Connect

**Campus Connect** is a full-stack, role-based web platform designed to centralize and simplify communication across a college campus. It enables students, faculty, visitors, and administrators to stay informed about campus events, opportunities, and announcements — all from one place.

> ✨ Built as a DBMS mini-project in the 4th semester by a team of three undergraduate students from Cummins College of Engineering for Women, Pune.

---

## 🔗 Live Demo

📂 [GitHub Repository](https://github.com/shreeya-malu/Campus_Connect)
> 🔔 **Note:** The live deployment is temporarily available at  
> 🌍 [https://campus-connect.onrender.com](https://campus-connect-zbf3.onrender.com/home)  
> *(It may be taken down soon)*

---

## 📌 Features Overview

### ✅ Homepage
- 📍 **Live Campus Map** (via OpenStreetMap): Displays ongoing events with location markers.
- 🗞️ **News Section**: View announcements, academic updates, placements, and other alerts.
- 🎉 **Events Section**: Highlights college events and programs at a glance.

### 👤 Role-Based Dashboards
- **Student View**:
  - Personalized dashboard with relevant news & event info.
- **Admin View**:
  - Access to:
    - ✅ News approval system
    - 📌 Event management (Add/Edit on map)
    - 📋 Activity logs (Track updates by users)
    - 🧩 Role-sensitive content visibility

### 📰 News Module
- 🎓 Filter news based on academic year.
- 📝 Submit **News Requests** for announcements to be verified and approved by admins.
- 🔁 Ensures democratized access to important updates — reducing dependency on fragmented sources like WhatsApp/Instagram.

---

## 🛠️ Tech Stack

| Layer        | Technologies Used                        |
|--------------|------------------------------------------|
| Frontend     | HTML, CSS, JavaScript                    |
| Backend      | Python, Flask                            |
| Database     | MySQL (hosted on [freesqldatabase.com](https://www.freesqldatabase.com)) |
| Hosting      | Render (Web App), GitHub (Source Code)   |
| Map          | OpenStreetMap (with Leaflet.js)          |

---

## 💡 Why Flask?

Flask was chosen for its:
- Lightweight and modular design, perfect for rapid prototyping.
- Easy integration with MySQL and frontend tech.
- Ideal balance between control and simplicity, making it suitable for academic-level full-stack development.

---

## 🚀 Deployment & Scalability

### Initial Setup:

* Originally built on local machines.
* Faced challenges:

  * Limited accessibility across systems.
  * Redundant code duplication.

### Final Solution:

* Migrated to cloud architecture:

  * 🔗 **Frontend + Backend** hosted on **Render**
  * 🗂️ **Database** on **freesqldatabase.com**
  * 🛠️ Codebase versioned and managed through **GitHub**

This transition ensured:

* Public access for demonstration and real use.
* Consistent output and collaboration.
* Scalability beyond classroom usage.

---

## 👥 Team Members

Shreeya Malu, Reema Desle, Ishwari Shekade

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/shreeya-malu/Campus_Connect.git
cd Campus_Connect
```

### 2. Install Dependencies

Create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # For Unix
venv\Scripts\activate     # For Windows

pip install -r requirements.txt
```

### 3. Configure Database

Update your DB credentials in `config.py`:

```python
DB_HOST = "sqlhost"
DB_USER = "username"
DB_PASSWORD = "password"
DB_NAME = "campusconnect"
```

### 4. Run the Application

```bash
python app.py
```

Then go to: `http://127.0.0.1:5000/`

---

## 🔐 Role-Based Access Guide

| Role    | Credentials (Default)                                    | Access                                    |
| ------- | -------------------------------------------------------- | ----------------------------------------- |
| Admin   | user_id: admin@gmail.com | password: admin@123           | Full access to approvals, logs, event map |

Students, Faculty can sign up and browse through the website or use Guest Login.

---

## 📈 Future Enhancements

* 🔐 OAuth / Google-based Login
* 📱 Mobile responsiveness
* 📢 Push notification system
* 📊 Admin analytics dashboard
* 🌍 Multilingual support

---

## 🗣️ Feedback & Contributions

We welcome contributions and ideas to improve Campus Connect!

Feel free to fork the repo, raise issues, or drop suggestions.

---

## 📝 License

This project is for academic and demonstration purposes. Please reach out before using it in production environments.

---


