// --- API base (GitHub Pages calls your local server) ---
const API_BASE = (window.location.hostname.endsWith("github.io"))
  ? "http://127.0.0.1:5000"  // when opened from GitHub Pages
  : "";                      // when served by Flask locally

// Then replace fetch("/search"...) with fetch(`${API_BASE}/search`, ...)
// and same for /summarize, /suggest, /health

let fullResults = [];
const resultsPerPage = 1;  // 1 document per page
let currentPage = 1;

// ---------------------- Utility Functions ----------------------
const predefinedSuggestions =[
  "Who is Daniel Radcliffe and why is he famous?",
  "What did Daniel Radcliffe do when he turned 18?",
  "How much money did Daniel Radcliffe inherit?",
  "What are Daniel Radcliffe's spending habits?",
  "Which movies has Daniel Radcliffe acted in besides Harry Potter?",
  "What is the plot of 'December Boys'?",
  "What is the TV film 'My Boy Jack' about?",
  "When did Daniel Radcliffe debut on stage?",
  "What records did 'Harry Potter and the Order of the Phoenix' break?",
  "How does Daniel Radcliffe deal with fame and media attention?",
  "What is the 'forgotten floor' in Miami-Dade jail?",
  "Why are mentally ill inmates kept on the ninth floor in Miami?",
  "Who is Judge Steven Leifman?",
  "Florida happenings",
  "What are 'avoidable felonies' and how do they happen?",
  "How do police confrontations affect mentally ill suspects?",
  "What is the mental health crisis in US jails?",
  "What crimes do many mentally ill inmates in Miami face?",
  "How does lack of treatment affect inmates with mental illness?",
  "What role does Soledad O'Brien play in covering this story?",
  "What reforms are proposed for handling mentally ill offenders?"
];
// Toggle theme
function toggleTheme() {
  document.documentElement.classList.toggle('dark');
  const theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  localStorage.setItem('theme', theme);
}

// Highlight query in snippet
function highlightText(snippet) {
  const query = document.getElementById("query")?.value.trim();
  if (!query) return snippet;
  return snippet.replace(new RegExp(query, "gi"), match => `<mark class='bg-yellow-200'>${match}</mark>`);
}

// Show / hide loading spinner
function showLoading(show) {
  const loading = document.getElementById("loadingMessage");
  if (loading) loading.classList.toggle("hidden", !show);
}

// Update local query history
function updateHistory(query) {
  const history = JSON.parse(localStorage.getItem("queryHistory") || "[]");
  if (!history.includes(query)) {
    history.unshift(query);
    if (history.length > 20) history.pop();
    localStorage.setItem("queryHistory", JSON.stringify(history));
  }
}
function suggestQueries() {
  const input = document.getElementById("query");
  if (!input) return;
  
  const query = input.value.toLowerCase();
  
  // Merge history and predefined
  const history = JSON.parse(localStorage.getItem("queryHistory") || "[]");
  const allSuggestions = [...new Set([...predefinedSuggestions, ...history])];

  const suggestions = allSuggestions
    .filter(q => q.toLowerCase().includes(query))
    .slice(0, 5);
  
  const container = document.getElementById("suggestions");
  if (!container) return;
  
  container.innerHTML = "";
  container.classList.toggle("hidden", suggestions.length === 0);

  suggestions.forEach(item => {
    const div = document.createElement("div");
    div.className = "cursor-pointer hover:text-blue-600 p-1";
    div.innerHTML = "🔍 " + item;
    div.onclick = () => {
      input.value = item;
      container.innerHTML = "";
      container.classList.add("hidden");
      searchAndSummarize();
    };
    container.appendChild(div);
  });
}
// ---------------------- Pagination ----------------------
function setupPagination() {
  const container = document.getElementById("pagination");
  if (!container) return;

  const totalPages = Math.ceil(fullResults.length / resultsPerPage);

  // Pagination always visible
  container.classList.remove("hidden");

  // Disable Prev/Next buttons when needed
  document.getElementById("prevPage").disabled = currentPage === 1;
  document.getElementById("nextPage").disabled = currentPage === totalPages;

  // Update page info
  document.getElementById("pageInfo").textContent = ` Page ${currentPage} of ${totalPages} `;
}

// Change page
function changePage(page) {
  const totalPages = Math.ceil(fullResults.length / resultsPerPage);
  if (page < 1 || page > totalPages) return;
  currentPage = page;
  displayResults();
  setupPagination();
}

// ---------------------- Display Results ----------------------
function displayResults() {
  const container = document.getElementById("results");
  if (!container) return;
  container.innerHTML = "";

  if (fullResults.length === 0) {
    container.innerHTML = "<p class='text-center text-gray-500'>😕 No results found.</p>";
    return;
  }

  const start = (currentPage - 1) * resultsPerPage;
  const visible = fullResults.slice(start, start + resultsPerPage);

  visible.forEach((doc, idx) => {
    const card = document.createElement("div");
    card.className = "bg-white p-5 rounded-lg shadow border border-gray-200 hover:shadow-md transition mb-3";
    card.innerHTML = `
      <div class="flex justify-between items-center mb-2">
        <h3 class="text-lg font-semibold text-gray-800">${doc.title || `Document ${start + idx + 1}`}</h3>
        <span class="text-sm text-gray-500">${Math.round((doc.relevanceScore || 0) * 100)}% match</span>
      </div>
      <p class="text-gray-700">${highlightText(doc.snippet || doc.text || "")}</p>
    `;
    container.appendChild(card);
  });
}

// ---------------------- Main Function ----------------------
function searchAndSummarize() {
  const queryInput = document.getElementById("query");
  const summaryLengthSelect = document.getElementById("summaryLength");
  const summaryDiv = document.getElementById("summary");
  const resultsContainer = document.getElementById("results");
  const paginationDiv = document.getElementById("pagination");

  if (!queryInput || !summaryLengthSelect || !summaryDiv || !resultsContainer || !paginationDiv) {
    console.error("Required DOM elements are missing!");
    return;
  }

  const query = queryInput.value.trim();
  const length = summaryLengthSelect.value;
  currentPage = 1;

  if (!query) return;

  showLoading(true);
  summaryDiv.classList.add("hidden");
  resultsContainer.innerHTML = "";
  paginationDiv.classList.add("hidden");

  // Fetch search results
  fetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: 5 })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Results received from backend:", data.results);

    fullResults = data.results || [];
    displayResults();
    setupPagination(); 
    if (fullResults.length === 0) {
      resultsContainer.innerHTML = `<p class='text-center text-gray-500'>😕 ${data.message || "No relevant documents found."}</p>`;
      summaryDiv.classList.add("hidden");
      showLoading(false);
      return;
    }

    updateHistory(query);

    return fetch("/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ documents: fullResults.map(d => d.text || d), length })
    });
  })
  .then(res => res?.json())
  .then(data => {
    if (!data) return;
    console.log("Summary received from backend:", data.summary);
    document.getElementById("summaryText").innerText = data.summary || "No summary generated.";
    summaryDiv.classList.remove("hidden");
    showLoading(false);
  })
  .catch(err => {
    console.error("Error during search or summarization:", err);
    resultsContainer.innerHTML = "<p class='text-center text-red-500'>Error during search or summarization.</p>";
    summaryDiv.classList.add("hidden");
    showLoading(false);
  });
}
