# BioScout: Biodiversity Observation Platform

BioScout is a Django-based biodiversity observation platform with a modern Flutter mobile app. It enables users to submit, view, validate, and analyze species observations, with AI-powered species suggestions, multilingual support, and robust permission controls. The mobile app works offline and syncs data when online.

---

## Features

### Web Platform (Django)
- User registration, login, and profile management (with profile pictures)
- Submit, update, and delete observations (with image upload)
- AI-powered species suggestions for uploaded images
- Validation and correction requests for observations
- Multilingual support and chatbot (RAG-QA) with translation
- Strong permission controls (only owners can edit/delete their observations)
- Modern, responsive UI with Bootstrap
- Landing page with featured observations, top validators, and most active observers
- Static and media file handling

### Mobile App (Flutter)
- **Offline-first:** Observations are stored locally and synced with the server when online
- User authentication (login, signup, logout)
- Submit new observations with images (camera/gallery)
- View list of all observations (with images, notes, sync status)
- View detailed observation info (AI suggestions, validations, corrections)
- Modern, responsive UI with green theme
- Pull-to-refresh and smooth navigation

---

## Project Structure

```
/Django Backend
├── bioscout/                # Django project settings
├── users/                   # User management app
├── observations/            # Observations app
├── rag_knowledge_base/      # RAG-QA chatbot
├── static/                  # Static files
├── media/                   # Uploaded images
├── db.sqlite3               # SQLite database
├── manage.py

/Flutter Mobile App
└── bioscout_mobile/
    ├── lib/
    │   ├── main.dart
    │   ├── screens/         # UI screens (login, register, home, add, details)
    │   ├── providers/       # State management (auth, observation)
    │   ├── services/        # API service
    │   └── database/        # Local SQLite helper
    ├── pubspec.yaml         # Flutter dependencies
    └── ...
```

---

## Getting Started

### Django Backend
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
3. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```
4. **Run the server:**
   ```bash
   python manage.py runserver
   ```

### Flutter Mobile App
1. **Install Flutter:** [Flutter Install Guide](https://docs.flutter.dev/get-started/install)
2. **Install dependencies:**
   ```bash
   cd bioscout_mobile
   flutter pub get
   ```
3. **Configure API URL:**
   - Create a `.env` file in `bioscout_mobile/` with:
     ```
     API_URL=http://<your-server-ip>:8000
     ```
   - (For Android emulator, use `http://10.0.2.2:8000`)
4. **Run the app:**
   ```bash
   flutter run
   ```

---

## Main Mobile App Features
- **Authentication:** Secure login, registration, and logout
- **Offline Observations:** Add observations offline; syncs automatically when online
- **Image Upload:** Attach photos from camera or gallery
- **Observation List:** View all observations with sync status
- **Details View:** See all info, AI suggestions, validations, and corrections
- **Modern UI:** Green theme, responsive design, smooth navigation

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License
[MIT](LICENSE) 