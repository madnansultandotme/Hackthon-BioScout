# BioScout Islamabad

**AI for Community Biodiversity & Sustainable Insights**

---

## 🌱 Overview
BioScout Islamabad is a community-driven, AI-powered web platform for biodiversity observation, education, and Q&A, focused on Islamabad and the Margalla Hills. Built for hackathons, it combines modern web tech, advanced RAG (Retrieval Augmented Generation) with Ollama (DeepSeek-r1), multilingual support, gamification, and PWA/offline capabilities.

---

## 🚀 Features
- **User Registration & Profile Management** (with badges for top observers and validators)
- **Biodiversity Observation Hub**
  - Submit observations (species, date, location, image, notes)
  - AI-powered species suggestion (mock/real)
  - Community validation (upvote AI suggestions)
  - Gamification: badges for top submitters and validators
- **Observation List & Map**
  - View all submissions with images, AI suggestions, and validation counts
- **RAG-Enhanced Q&A System**
  - Ask biodiversity questions (English/Urdu)
  - Advanced RAG: context retrieval + Ollama DeepSeek-r1 LLM answers
- **Multilingual UI** (English/Urdu toggle)
- **PWA/Offline Support** (installable, works offline)
- **Modern, Eye-Catching UI** (Bootstrap, icons, hero banners, cards)

---

## 🛠️ Setup & Installation
1. **Clone the repo & install dependencies:**
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   python -m venv venv
   venv/Scripts/activate  # or source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Install Ollama & DeepSeek-r1 model (for advanced RAG):**
   - [Ollama install guide](https://ollama.com/download)
   - Run: `ollama pull deepseek-coder:latest` (or `deepseek-r1`)
   - Start Ollama: `ollama serve`
3. **Run Django migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the server:**
   ```bash
   python manage.py runserver
   ```
6. **Access the app:**
   - Web: [http://localhost:8000/](http://localhost:8000/)
   - Swagger API: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

---

## 🌍 Demo Flow
1. **Register/Login** (English or Urdu)
2. **Submit an Observation** (species, image, notes, etc.)
3. **See AI Suggestion & Validate** (upvote, earn badges)
4. **Ask Biodiversity Questions** (Q&A, RAG with LLM, Urdu/English)
5. **Switch Languages** (toggle in navbar)
6. **Install as PWA** (add to home screen, demo offline)
7. **View Profile & Badges**

---

## 📦 Project Structure
- `users/` — User management, profiles, badges
- `observations/` — Observation submission, validation, API, Q&A
- `rag_knowledge_base/` — Knowledge base and FAQ for RAG
- `manifest.json`, `sw.js` — PWA support
- `templates/` — Bootstrap, multilingual, and modern UI

---

## 🤖 AI & RAG Details
- **RAG Q&A:**
  - Retrieves context from curated knowledge base and FAQ
  - Sends context + question to Ollama (DeepSeek-r1) for expert answer
  - Falls back to context-only answer if LLM is unavailable
- **AI Species Suggestion:**
  - Mocked for demo, can be replaced with real API/model

---

## 🏆 Hackathon Tips
- Highlight multilingual, PWA, and advanced RAG features
- Show badges, validation, and community engagement
- Demo offline install and Urdu/English toggle
- Explain how the system can scale (add real AI, more languages, maps, etc.)

---

## 📄 License
MIT (or specify your own)

---

## 🌐 Web vs. API Endpoints
- **Web Endpoints (for browser/HCI):**
  - `/profile/` — User profile (with observations, badges, etc.)
  - `/observations/list/` — All observations (web)
  - `/register/`, `/login/`, `/logout/` — Web auth
  - `/rag-qa/` — Q&A (web)
- **API Endpoints (for mobile/app):**
  - `/api/users/profile/` — User profile (API, JSON)
  - `/api/users/register/`, `/api/users/login/` — API auth
  - `/observations/api/` — Observations API (list/create)
  - `/observations/api/<id>/` — Observation detail (API) 