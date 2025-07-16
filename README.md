# Campus Connect

**Campus Connect** is a centralized platform that connects students, professors, and administrators by streamlining communication, academic collaboration, and opportunity sharing — all within one unified system.

> 🔔 **Note:** The live deployment is temporarily available at  
> 🌍 [https://campus-connect.onrender.com](https://campus-connect-zbf3.onrender.com/home)  
> *(It may be taken down soon)*
---
# 🎓 Campus Connect

**Campus Connect** is a full-stack, role-based web platform designed to centralize and simplify communication across a college campus. It enables students, faculty, visitors, and administrators to stay informed about campus events, opportunities, and announcements — all from one place.

> ✨ Built as a DBMS mini-project in the 4th semester by a team of three undergraduate students from Cummins College of Engineering for Women, Pune.

---

## 🔗 Live Demo

🚀 [Hosted on Render](https://your-link-here.com)  
📂 [GitHub Repository](https://github.com/shreeya-malu/Campus_Connect)

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

## 🌐 Architecture Diagram

```mermaid
graph TD;
  A[User] --> B[Frontend - HTML/CSS/JS]
  B --> C[Flask Backend]
  C --> D[MySQL Database (Cloud Hosted)]
  C --> E[Render (Deployed Platform)]
````

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

| Name                | Role                                                                   |
| ------------------- | ---------------------------------------------------------------------- |
| **Shreeya Malu**    | Homepage, News Module, DB Integration, Cloud Migration, Admin Features |
| **Reema Desle**     | \[Details of her work, optional]                                       |
| **Ishwari Shekade** | \[Details of her work, optional]                                       |

> 🙌 Special thanks to my team — the project was a true collaboration of skills, creativity, and commitment.

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
| Admin   | [admin@example.com](mailto:admin@example.com) / admin    | Full access to approvals, logs, event map |
| Student | [student@example.com](mailto:student@example.com) / pass | Limited dashboard, news/event view only   |

---

## 📦 Folder Structure

```
Campus_Connect/
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── ...
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

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


