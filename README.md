## 🌍 EcoTrack – Carbon Footprint Monitoring App

A modern mobile app that empowers users to track, understand, and reduce their carbon footprint.

EcoTrack combines a sleek Flutter mobile UI, a robust FastAPI backend, and real-world emissions data (including 2026 vehicle datasets from fueleconomy.gov) to provide accurate environmental impact insights.

## ✨ Features
# 📱 Flutter Mobile App

Smooth & responsive UI

Activity-based footprint tracking

Vehicle emission lookup (using 2026 dataset)

Persistent login using JWT

Offline-friendly design

Easily shareable APK builds (no Play Store needed)

# ⚙️ FastAPI Backend

Fast, modern Python API

Secure authentication (JWT)

PostgreSQL database hosted on Render

Seeded emissions dataset for vehicles & activities

Extensible modular architecture (routers, services, DB layer)

# 🔒 Authentication

Email + password (JWT)

Upcoming: Firebase OTP login, signup & password reset

# 📊 Roadmap Features

Full analytics dashboard

Emission trends & charts

User badges, achievements & streaks

Recommendation engine for sustainable habits

Profile screen redesign

# 🖼️ Screenshots



Car Tab
![Screenshot_2025-11-20-12-15-31-80_6fadc5a6af6d61dfdadcfcc4e0542daa](https://github.com/user-attachments/assets/c1c38834-429d-4dba-ba51-46d760f39c10)

Summary
![Screenshot_2025-11-20-12-15-48-25_6fadc5a6af6d61dfdadcfcc4e0542daa](https://github.com/user-attachments/assets/73a841d8-182d-45b7-b6ed-e7d10e8a7b42)

	
	
Recommendation and Badges
![Screenshot_2025-11-20-12-18-07-43_6fadc5a6af6d61dfdadcfcc4e0542daa](https://github.com/user-attachments/assets/d81cc37d-1fca-4558-8bbe-ba669dc20dc4)

	
	
# 🧱 Project Structure

``Carbon_Footprint_App/
│
├── FRONTEND/               # Flutter mobile application
│   ├── lib/
│   │   ├── screens/
│   │   ├── widgets/
│   │   └── services/
│   ├── android/
│   ├── ios/                # Buildable only via macOS
│   └── pubspec.yaml
│
├── BACKEND/                # FastAPI server
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   ├── db/
│   │   
│   |
│   ├── requirements.txt
│   └── .env (ignored)
│
└── README.md
``

# ⚙️ Setup Instructions
🔧 Backend (FastAPI)
```
git clone https://github.com/Rennar77/carbon-footprint-app.git
cd carbon-footprint-app/BACKEND


python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URLs:

API Root → http://localhost:8000

Docs → http://localhost:8000/docs

# 📱 Frontend (Flutter)
```
cd ../FRONTEND

flutter pub get
flutter run
```

# To build an APK:
``
flutter build apk --release
``


APK output path:

FRONTEND/build/app/outputs/flutter-apk/app-release.apk


You can share this file directly with friends.

# 🧪 Tech Stack
Mobile

Flutter (Dart)

Material Design 3

Backend

FastAPI

Python 3.11

Uvicorn

JWT (jose + passlib)

Database

PostgreSQL (Render)

Custom-seeded vehicle dataset (2026 models)

Auth

JWT (current)

Firebase OTP (planned)

## 🗺️ Roadmap
# 🚀 In Development

Fixing profile bugs from deployment

Adding forgot-password screen

Integrating Firebase OTP (auth overhaul)

# 🔜 Future Enhancements

Analytics graphs (weekly/monthly footprint)

Streaks & achievements

Improved recommendation engine

CO₂ budgets + gamification

Auto-sync across devices

# 🤝 Contributing

Fork this repository

Create a feature branch

Commit your changes

Submit a Pull Request

# 📄 License

MIT License — free for personal and commercial use.
