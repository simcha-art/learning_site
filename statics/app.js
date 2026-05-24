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
    question.options.forEach((option) => {
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
