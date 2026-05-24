import os
import sys
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = {
    os.path.join(TEMPLATE_DIR, "index.html"): """
<!DOCTYPE html>
<html lang="he">
<head>
  <meta charset="UTF-8" />
  <title>אתר למידה פרקי</title>
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <div class="page shell">
    <header class="topbar">
      <div>
        <h1>אתר למידה לפי פרקים</h1>
        <p>בחר פרק וגש לחומר, סיכום, מבחנים ושאלות פתוחות.</p>
      </div>
    </header>

    <main>
      <section class="intro-box">
        <h2>מבנה הפרקים</h2>
        <p>כל פרק מכיל חומר לימודי, סיכום, מבחן אמריקאי כללי, מבחן פרטני ושאלות פתוחות.</p>
      </section>

      <section id="chapter-list" class="chapter-grid"></section>
    </main>

    <footer class="footer">
      <p>האתר נבנה כסלייד ללמידה עם תשתית דו-כיוונית עבור תוכן עתידי.</p>
    </footer>
  </div>

  <script src="/static/app.js"></script>
</body>
</html>
""",
    os.path.join(TEMPLATE_DIR, "chapter.html"): """
<!DOCTYPE html>
<html lang="he">
<head>
  <meta charset="UTF-8" />
  <title>פרק - אתר למידה</title>
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <div class="page shell">
    <header class="topbar">
      <div>
        <a class="back-link" href="/">← חזרה לתפריט הפרקים</a>
        <h1 id="chapter-title">טוען פרק...</h1>
        <p id="chapter-subtitle"></p>
      </div>
    </header>

    <main>
      <section class="section-box">
        <h2>חומר לימודי</h2>
        <div id="chapter-content" class="content-box"></div>
      </section>

      <section class="section-box">
        <h2>סיכום</h2>
        <div id="chapter-summary" class="content-box"></div>
      </section>

      <section class="section-box">
        <h2>שאלות ל־AI</h2>
        <p>שאל כל שאלה על החומר או על מושג מסוים בפרק.</p>
        <textarea id="ai-question-input" rows="4" placeholder="כתוב כאן שאלה על החומר..."></textarea>
        <button id="ask-ai-button" class="primary-button">שלח שאלה ל‑AI</button>
        <div id="ai-answer-output" class="output-box"></div>
      </section>

      <section class="section-box">
        <h2>מבחן אמריקאי כללי</h2>
        <div id="general-quiz" class="quiz-box"></div>
        <button id="general-submit" class="primary-button">בדוק מבחן כללי</button>
        <div id="general-result" class="result-box"></div>
      </section>

      <section class="section-box">
        <h2>מבחן אמריקאי פרטני</h2>
        <div id="detailed-quiz" class="quiz-box"></div>
        <button id="detailed-submit" class="primary-button">בדוק מבחן פרטני</button>
        <div id="detailed-result" class="result-box"></div>
      </section>

      <section class="section-box">
        <h2>מבחן שאלות פתוחות</h2>
        <div id="open-question-area"></div>
        <button id="open-submit" class="primary-button">בדוק תשובה ב‑AI</button>
        <div id="open-result" class="result-box"></div>
      </section>
    </main>

    <footer class="footer">
      <p>המערכת עדיין בשלד; תוכל לשלב את ה‑AI מאוחר יותר.</p>
    </footer>
  </div>

  <script src="/static/app.js"></script>
</body>
</html>
""",
    os.path.join(STATIC_DIR, "styles.css"): """
:root {
  --bg: #0f172a;
  --surface: #111827;
  --surface-2: #1e293b;
  --text: #e2e8f0;
  --accent: #38bdf8;
  --accent-2: #34d399;
  --border: #334155;
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
a {
  color: var(--accent);
  text-decoration: none;
}
.shell {
  width: min(1100px, 96%);
  margin: 0 auto;
  padding: 24px 0;
}
.topbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.back-link {
  color: var(--accent-2);
}
.chapter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
}
.chapter-card, .section-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px;
}
.chapter-card h3 {
  margin: 0 0 10px;
  color: var(--accent-2);
}
.chapter-card p {
  margin: 0 0 12px;
}
.chapter-card a {
  display: inline-block;
  margin-top: 10px;
  padding: 10px 16px;
  background: var(--accent);
  border-radius: 12px;
  color: #0f172a;
  font-weight: bold;
}
.content-box, .output-box, .result-box {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  margin-top: 12px;
}
textarea, input[type=text] {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: #0f172a;
  color: var(--text);
  margin-top: 10px;
  resize: vertical;
}
.primary-button {
  border: none;
  background: var(--accent-2);
  color: #0f172a;
  font-weight: bold;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  margin-top: 16px;
}
.primary-button:hover {
  opacity: 0.9;
}
.quiz-box {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.quiz-question {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
}
.quiz-question h4 {
  margin: 0 0 10px;
}
.option-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
@media (max-width: 720px) {
  .chapter-grid {
    grid-template-columns: 1fr;
  }
}
""",
    os.path.join(STATIC_DIR, "app.js"): """
let chaptersData = [];
let currentChapter = null;

async function fetchChapters() {
  const response = await fetch('/data/chapters.json');
  return response.json();
}

async function loadChapterList() {
  const data = await fetchChapters();
  chaptersData = data.chapters;
  const list = document.getElementById('chapter-list');
  list.innerHTML = '';
  chaptersData.forEach((chapter) => {
    const card = document.createElement('div');
    card.className = 'chapter-card';
    card.innerHTML = `
      <h3>${chapter.title}</h3>
      <p>${chapter.subtitle}</p>
      <a href="/chapter.html?id=${encodeURIComponent(chapter.id)}">פתח פרק</a>
    `;
    list.appendChild(card);
  });
}

function getQueryParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

async function initChapterPage() {
  const chapterId = getQueryParam('id');
  if (!chapterId) {
    document.getElementById('chapter-title').textContent = 'פרק לא נמצא';
    return;
  }
  const data = await fetchChapters();
  chaptersData = data.chapters;
  currentChapter = chaptersData.find((chapter) => chapter.id === chapterId);
  if (!currentChapter) {
    document.getElementById('chapter-title').textContent = 'פרק לא נמצא';
    return;
  }
  renderChapter();
}

function renderChapter() {
  document.getElementById('chapter-title').textContent = currentChapter.title;
  document.getElementById('chapter-subtitle').textContent = currentChapter.subtitle;
  document.getElementById('chapter-content').textContent = currentChapter.content;
  document.getElementById('chapter-summary').textContent = currentChapter.summary;

  renderQuiz('general-quiz', currentChapter.generalQuiz);
  renderQuiz('detailed-quiz', currentChapter.detailedQuiz);

  renderOpenQuestion();
  setupAIQuestion();
  document.getElementById('general-submit').onclick = submitGeneralQuiz;
  document.getElementById('detailed-submit').onclick = submitDetailedQuiz;
  document.getElementById('open-submit').onclick = submitOpenQuestion;
  document.getElementById('ask-ai-button').onclick = askAIQuestion;
}

function renderQuiz(containerId, questions) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  questions.forEach((question, index) => {
    const questionCard = document.createElement('div');
    questionCard.className = 'quiz-question';
    questionCard.innerHTML = `
      <h4>שאלה ${index + 1}: ${question.question}</h4>
      <div id="${containerId}-question-${index}"></div>
    `;
    container.appendChild(questionCard);

    const optionsDiv = questionCard.querySelector(`#${containerId}-question-${index}`);
    question.options.forEach((option, optionIndex) => {
      const optionRow = document.createElement('label');
      optionRow.className = 'option-row';
      optionRow.innerHTML = `
        <input type="radio" name="${containerId}-q-${index}" value="${option}" />
        <span>${option}</span>
      `;
      optionsDiv.appendChild(optionRow);
    });
  });
}

function renderOpenQuestion() {
  const container = document.getElementById('open-question-area');
  container.innerHTML = '';
  currentChapter.openQuestions.forEach((question) => {
    const questionBlock = document.createElement('div');
    questionBlock.className = 'quiz-question';
    questionBlock.innerHTML = `
      <h4>${question.question}</h4>
      <textarea id="open-answer-${question.id}" rows="5" placeholder="הזן כאן את תשובתך..."></textarea>
    `;
    container.appendChild(questionBlock);
  });
}

function setupAIQuestion() {
  const input = document.getElementById('ai-question-input');
  if (currentChapter.aiTopics && currentChapter.aiTopics.length) {
    input.placeholder = 'שאל על מושג או חלק מהחומר, לדוגמה: ' + currentChapter.aiTopics.join(' / ');
  }
}

function submitGeneralQuiz() {
  const result = gradeQuiz('general-quiz', currentChapter.generalQuiz);
  document.getElementById('general-result').innerHTML = result;
}

function submitDetailedQuiz() {
  const result = gradeQuiz('detailed-quiz', currentChapter.detailedQuiz);
  document.getElementById('detailed-result').innerHTML = result;
}

function gradeQuiz(sectionId, questions) {
  let score = 0;
  let answered = 0;
  questions.forEach((question, index) => {
    const selected = document.querySelector(`input[name="${sectionId}-q-${index}"]:checked`);
    if (selected) {
      answered += 1;
      if (selected.value === question.answer) {
        score += 1;
      }
    }
  });
  const percent = questions.length ? Math.round((score / questions.length) * 100) : 0;
  return `<strong>תוצאה:</strong> ${score} מתוך ${questions.length} (${percent}%)<br>נענו ${answered} שאלות.`;
}

function submitOpenQuestion() {
  const resultBox = document.getElementById('open-result');
  const feedback = [];
  currentChapter.openQuestions.forEach((question) => {
    const answer = document.getElementById(`open-answer-${question.id}`).value.trim();
    if (!answer) {
      feedback.push(`<p><strong>${question.question}</strong><br>לא הוזנה תשובה.</p>`);
      return;
    }
    const evaluation = evaluateOpenQuestion(question.question, answer, question.referenceAnswer);
    feedback.push(`<div class="output-box">
      <h4>${question.question}</h4>
      <p><strong>ציון מדומה:</strong> ${evaluation.score}%</p>
      <p><strong>האם תואם:</strong> ${evaluation.isCorrect ? 'כן' : 'לא'}</p>
      <p><strong>הערות:</strong> ${evaluation.feedback}</p>
      <p><strong>התשובה השמורה:</strong> ${question.referenceAnswer}</p>
    </div>`);
  });
  resultBox.innerHTML = feedback.join('');
}

function evaluateOpenQuestion(question, studentAnswer, referenceAnswer) {
  const normalize = (text) => text
    .toLowerCase()
    .replace(/[^\\wא-ת\\s]/g, ' ')
    .split(/\\s+/)
    .filter(Boolean);

  const studentWords = new Set(normalize(studentAnswer));
  const referenceWords = normalize(referenceAnswer);
  const matches = referenceWords.filter((word) => studentWords.has(word));
  const score = referenceWords.length ? Math.round((matches.length / referenceWords.length) * 100) : 0;
  const isCorrect = score >= 60;

  let feedback = 'התשובה עדיין לא נבחנה על ידי AI אמיתי.';
  if (isCorrect) {
    feedback = 'התשובה שלך נראית מתאימה לרוב התשובה השמורה.';
  } else {
    feedback = 'יש פערים בתשובה. נסה להתמקד בנקודות המרכזיות והפרטים המצוינים בתשובה השמורה.';
  }

  return {
    score,
    isCorrect,
    feedback,
  };
}

function askAIQuestion() {
  const question = document.getElementById('ai-question-input').value.trim();
  const output = document.getElementById('ai-answer-output');
  if (!question) {
    output.textContent = 'אנא הזן שאלה לפני שליחה.';
    return;
  }

  output.innerHTML = '<em>שולח שאלה ל‑AI...</em>';
  setTimeout(() => {
    output.innerHTML = `
      <p><strong>AI:</strong> זהו תיאור דוגמה של תשובה. כאשר תוסיף חיבור ל‑AI אמיתי, כאן תוצג התשובה.</p>
      <p>השאלה שנשלחה: ${question}</p>
    `;
  }, 500);
}

window.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('chapter-list')) {
    loadChapterList();
  }
  if (document.getElementById('chapter-title')) {
    initChapterPage();
  }
});
""",
    os.path.join(DATA_DIR, "chapters.json"): """
{
  "chapters": [
    {
      "id": "chapter-1",
      "title": "פרק 1 - מבוא ללמידה",
      "subtitle": "הרעיון הכללי של בניית אתר למידה",
      "content": "זהו חומר דוגמה עבור מפרק ראשון. כאן נמצא הטקסט המקורי על הנושא. ניתן לשים כאן קטע ממאמר, ספר או מערך שיעור. המטרה היא להראות את מבנה הדף ואת מה שקורא המשתמש.",
      "summary": "הפרק מסביר את מבנה האתר, את הנקודות המרכזיות שצריך ללמוד ואת האופן שבו סוגי המבחנים השונים פועלים.",
      "aiTopics": [
        "כיצד לשאול שאלה על חומר",
        "איך לבחור תשובה נכונה במבחן אמריקאי",
        "מה ההבדל בין מבחן כללי למבחן פרטני"
      ],
      "generalQuiz": [
        {
          "id": "g1",
          "question": "מה המטרה הראשית של אתר הלמידה?",
          "options": [
            "להציג פרקים עם חומר וסיכומים",
            "להחליף מישהו שקורא את החומר",
            "לפתור תרגילי מתמטיקה בלבד",
            "ליצור רשת חברתית"
          ],
          "answer": "להציג פרקים עם חומר וסיכומים"
        },
        {
          "id": "g2",
          "question": "מה אפשר למצוא בכל פרק באתר?",
          "options": [
            "חומר לימודי, סיכום ושאלות פתוחות",
            "רק סרטונים",
            "רק קבצי PDF להורדה",
            "משחקים אינטראקטיביים בלבד"
          ],
          "answer": "חומר לימודי, סיכום ושאלות פתוחות"
        }
      ],
      "detailedQuiz": [
        {
          "id": "d1",
          "question": "מהו המבחן הפרטני?",
          "options": [
            "מבחן שמרכז את כל התוכן",
            "מבחן עם שאלות שעוברות על פרטים ספציפיים",
            "מבחן חדר כושר",
            "שאלון חוויתי בלבד"
          ],
          "answer": "מבחן עם שאלות שעוברות על פרטים ספציפיים"
        },
        {
          "id": "d2",
          "question": "איזו דרך עבודה מבוצעת במבחן פתוח?",
          "options": [
            "המשתמש בוחר תשובה מרובת אפשרויות",
            "המשתמש מזין תשובה חופשית",
            "אין תשובות לשאלה",
            "התשובה נכתבת ע"י המערכת בלבד"
          ],
          "answer": "המשתמש מזין תשובה חופשית"
        }
      ],
      "openQuestions": [
        {
          "id": "o1",
          "question": "נסח בקצרה את המטרה של אתר הלמידה הזה.",
          "referenceAnswer": "המטרה היא לאפשר כניסה נוחה לחומר לימוד לפי פרקים, לספק סיכומים, מבחנים אמריקאיים ושאלות פתוחות עם בדיקת AI."
        }
      ]
    },
    {
      "id": "chapter-2",
      "title": "פרק 2 - איך בונים פרק",
      "subtitle": "הכנת חומר, סיכום ומבחנים",
      "content": "בחלק זה נסביר כיצד נכון לארגן את התוכן של פרק: חומר מקורי, סיכום, שאלות קישוריות ושאלות לבדיקת הבנה.",
      "summary": "פרק זה עוסק בתהליך יצירת פרק: מבנה, חלוקה מתודית ויצירת מבחנים המתאימים לשלבים שונים של הלמידה.",
      "aiTopics": [
        "כיצד לנסח שאלה פתוחה",
        "מה הם מרכיבי סיכום טוב",
        "איך להעריך תשובות פתוחות"
      ],
      "generalQuiz": [
        {
          "id": "g3",
          "question": "מה צריך לכלול סיכום טוב?",
          "options": [
            "נקודות מרכזיות ותשובות",
            "תיאור ארוך בלי תמצות",
            "רק טבלה של נקודות",
            "תוכן לא קשור"
          ],
          "answer": "נקודות מרכזיות ותשובות"
        }
      ],
      "detailedQuiz": [
        {
          "id": "d3",
          "question": "למה חשוב לשלב שאלות פתוחות בפרק?",
          "options": [
            "כדי לבדוק הבנה עמוקה",
            "כדי להאריך את המסמך",
            "כדי להסתיר תוכן",
            "כדי לא לפתח חשיבה"
          ],
          "answer": "כדי לבדוק הבנה עמוקה"
        }
      ],
      "openQuestions": [
        {
          "id": "o2",
          "question": "תאר את שלב הסיכום בפרק במילים שלך.",
          "referenceAnswer": "שלב הסיכום צריך לזקק את עיקרי הדברים, להסביר בקיצור את המסקנות ולתת לנבחן ראייה ברורה של הנושא."
        }
      ]
    }
  ]
}
"""
}


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write(content.lstrip("\n"))
        print(f"Created {path}")
    else:
        print(f"Skipped existing file: {path}")


def create_skeleton():
    for path, content in FILES.items():
        write_file(path, content)

    print("\nSkeleton complete.")
    print("להפעלת האתר המקומי, הרץ:\n  python main.py serve")
    print("ואז פתח בדפדפן:\n  http://localhost:8000\n")


def start_server(port=8000):
    os.chdir(BASE_DIR)
    handler = SimpleHTTPRequestHandler
    with TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nServer stopped.")


def main():
    create_skeleton()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        start_server()


if __name__ == "__main__":
    main()