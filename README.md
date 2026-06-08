# 🎓 Student Profile Analyzer

A Streamlit app that lets you search for a student by name from the AIML 2027 dataset and view their full profile + Claude AI-powered analysis.

---

## 📁 Files Needed

```
project/
├── app.py
├── requirements.txt
└── student_data.xlsx        ← your uploaded Excel file (rename it to this)
```

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Place your Excel file
Rename your file to `student_data.xlsx` and put it in the same folder as `app.py`.

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🔑 API Key

- Get your Anthropic API key from: https://console.anthropic.com/
- Paste it into the **sidebar** of the app when it opens
- The key is never stored — it's only used for the current session

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔍 Name Search | Exact or partial/fuzzy match |
| 📊 Academic View | 10th, 12th, CGPA, all semester GPAs, arrears |
| 🪪 Personal Info | DOB, city, parents, contact, email |
| 💻 Tech Stack | Parsed tech tags + GitHub + Resume links |
| 🤖 AI Analysis | Claude gives academic snapshot, strengths, career fit & tip |

---

## 💡 Tips

- Use **Partial / Fuzzy** mode to find students by first name only
- Multiple results are shown if more than one name matches
- AI analysis is skipped gracefully if no API key is provided
