# 🃏 Flashcard Quiz App

> **Internship / Portfolio Project** · Built with Python 3 & Streamlit

---

## 📌 Project Description

**Flashcard Quiz App** is a full-featured, production-quality educational web application built with Python and Streamlit. It allows users to create, manage, study, and quiz themselves on flashcards across multiple categories and difficulty levels — all wrapped in a polished dark/light-mode UI with animated cards, interactive charts, and persistent local storage.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🃏 Flashcard CRUD | Create, edit, delete, view all cards |
| 📁 Import / Export | Upload or download JSON flashcard sets |
| 💾 Persistent Storage | Cards saved permanently to `flashcards.json` |
| 📖 Study Mode | One card at a time, flip animation, shuffle, category/difficulty filter |
| 🎯 Quiz Mode | Multiple-choice quiz, scoring, review, performance summary |
| 📊 Statistics | Charts for category breakdown, difficulty distribution, score history |
| ⭐ Favorites | Mark, browse, and remove favorite cards |
| 🔍 Search & Filter | By question, answer, category, and difficulty |
| 🌙 Dark / Light Mode | One-click theme toggle |
| 📱 Responsive UI | Works on desktop, tablet, and mobile browsers |
| 🗂 6 Categories | Programming, Mathematics, Science, General Knowledge, History, Custom |
| 📈 Progress Tracking | Studied count, quiz attempts, average score, accuracy |

---

## 📁 Folder Structure

```
FlashcardQuizApp/
│
├── app.py              # Main Streamlit application (~600 lines)
├── flashcards.json     # 105 sample flashcards (persistent storage)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation (this file)
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/FlashcardQuizApp.git
cd FlashcardQuizApp
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Run Command

```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 📖 Usage

### Dashboard
- Overview of all statistics and recently added cards
- Category bar chart and difficulty pie chart

### Study Mode
- Filter by category, difficulty, or favorites
- Click **Flip Card** to reveal the answer
- Navigate with Previous / Next, or Shuffle for random order
- Cards are marked as "studied" when flipped

### Quiz Mode
1. Set category, difficulty, and number of questions
2. Click **Start Quiz**
3. Choose the correct answer from 4 options
4. View score, percentage, and per-question review at the end

### Manage Cards
- **All Cards tab**: View, search, edit, delete, and favorite any card
- **Add New Card tab**: Create a card with question, answer, category, difficulty
- **Import/Export tab**: Download all cards as JSON or upload a JSON file

### Favorites
- View all starred cards
- Filter by category
- Remove from favorites

### Statistics
- Total/studied cards per category (grouped bar chart)
- Difficulty distribution (bar chart)
- Quiz score history (line chart)
- Detailed quiz attempt history table

---

## 🖼 Screenshots

> _Add screenshots after running the app locally._

| Dashboard (Dark) | Study Mode | Quiz Mode |
|---|---|---|
| _(screenshot)_ | _(screenshot)_ | _(screenshot)_ |

| Manage Cards | Statistics | Favorites |
|---|---|---|
| _(screenshot)_ | _(screenshot)_ | _(screenshot)_ |

**How to capture:**
1. Run `streamlit run app.py`
2. Use your OS snipping tool or browser screenshot
3. Replace the placeholders above

---

## 🛠 Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **Streamlit 1.32+** | Web application framework |
| **Plotly 5.18+** | Interactive charts (bar, pie, line) |
| **JSON** | Persistent local flashcard storage |
| **CSS3** | Custom styling, animations, dark/light themes |
| **Google Fonts** | Syne (headings) + Mulish (body) |
| **Streamlit Session State** | Quiz score, favorites, theme, navigation |
| **uuid** | Unique card ID generation |

---

## 🔮 Future Enhancements

- [ ] User authentication with per-user card collections
- [ ] Spaced repetition algorithm (SM-2) for smarter study scheduling
- [ ] Text-to-speech card reading
- [ ] Image support on flashcard faces
- [ ] Multiplayer quiz mode (WebSockets)
- [ ] Cloud sync (Firebase / Supabase backend)
- [ ] AI-powered flashcard generation from uploaded documents
- [ ] Mobile app version (Kivy / React Native)
- [ ] Export quiz results as PDF report
- [ ] Streak tracking and gamification badges

---

## 👤 Author

**Your Name**
- 🌐 Portfolio: [yourwebsite.com](https://yourwebsite.com)
- 💼 LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- 🐙 GitHub: [github.com/yourusername](https://github.com/yourusername)
- 📧 Email: your.email@example.com

---

## 📤 GitHub Repository Setup

```bash
# 1. Initialise git
git init

# 2. Stage all files
git add .

# 3. Initial commit
git commit -m "feat: initial release — Flashcard Quiz App"

# 4. Link remote
git remote add origin https://github.com/yourusername/FlashcardQuizApp.git

# 5. Push
git branch -M main
git push -u origin main
```

**Recommended repo settings:**
- ✅ Description: *"Flashcard Quiz App — Python Internship Portfolio Project"*
- ✅ Topics: `python` `streamlit` `flashcards` `quiz` `education` `internship` `plotly`
- ✅ Add a `LICENSE` file (MIT recommended)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ using Python &amp; Streamlit · Internship Project 2024
</div>
