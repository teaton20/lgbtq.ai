document.addEventListener("DOMContentLoaded", function() {
  const progressOverlay = document.getElementById("progress-overlay");
  const progressMessage = document.getElementById("progress-message");
  const getArticlesBtn = document.getElementById("get-articles-btn");
  const analyzeBtn = document.getElementById("analyze-btn");
  const articleForm = document.getElementById("article-form");
  const analyzeForm = document.getElementById("analyze-form");
  const resultsSection = document.getElementById("results");
  const url1Input = document.getElementById("url1");
  const url2Input = document.getElementById("url2");
  const text1Input = document.getElementById("text1");
  const text2Input = document.getElementById("text2");

  const progressMessages = [
    "Loading models... Hang tight while we initialize.",
    "Computing semantic similarity... Just a moment!",
    "Analyzing tone and style for Article 1... Almost there!",
    "Analyzing tone and style for Article 2... Please wait!",
    "Generating comparative analysis... Hold on tight!",
    "Classifying emotions... Almost finished!",
    "Running guardrail checks... Finalizing results..."
  ];
  let messageIndex = 0;
  let progressInterval = null;

  function startProgressUpdates() {
    progressOverlay.style.display = "flex";
    progressMessage.textContent = progressMessages[messageIndex];
    progressInterval = setInterval(() => {
      messageIndex = (messageIndex + 1) % progressMessages.length;
      progressMessage.textContent = progressMessages[messageIndex];
    }, 4000);
  }

  function stopProgressUpdates() {
    clearInterval(progressInterval);
    messageIndex = 0;
    progressMessage.textContent = progressMessages[0];
    progressOverlay.style.display = "none";
  }

  function validateURL(url) {
    // Basic URL validation regex
    const regex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/;
    return regex.test(url);
  }

  // Disable form inputs during an AJAX call
  function setFormDisabled(form, disabled) {
    Array.from(form.elements).forEach(el => el.disabled = disabled);
  }

  // "Get Articles" button event
  getArticlesBtn.addEventListener("click", function(e) {
    e.preventDefault();
    const url1 = url1Input.value.trim();
    const url2 = url2Input.value.trim();

    if (!url1 && !url2) {
      alert("Please enter at least one URL.");
      return;
    }
    if (url1 && !validateURL(url1)) {
      alert("Article URL 1 is invalid.");
      return;
    }
    if (url2 && !validateURL(url2)) {
      alert("Article URL 2 is invalid.");
      return;
    }

    startProgressUpdates();
    setFormDisabled(articleForm, true);

    const formData = new FormData();
    formData.append("url1", url1);
    formData.append("url2", url2);

    fetch("/get_articles", {
      method: "POST",
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Error fetching articles.");
      }
      return response.json();
    })
    .then(data => {
      stopProgressUpdates();
      setFormDisabled(articleForm, false);
      if (data.error) {
        alert(data.error);
      } else {
        text1Input.value = data.text1;
        text2Input.value = data.text2;
      }
    })
    .catch(error => {
      console.error("Error fetching articles:", error);
      stopProgressUpdates();
      setFormDisabled(articleForm, false);
      alert("An error occurred while fetching articles.");
    });
  });

  // "Analyze" form submission event
  analyzeForm.addEventListener("submit", function(e) {
    e.preventDefault();
    if (!text1Input.value.trim() || !text2Input.value.trim()) {
      alert("Both article texts are required for analysis.");
      return;
    }

    startProgressUpdates();
    setFormDisabled(analyzeForm, true);

    // Create FormData from the analyze form and manually add text1, text2, and guardrail_questions values.
    const formData = new FormData(analyzeForm);
    formData.append("text1", text1Input.value);
    formData.append("text2", text2Input.value);
    // Explicitly append guardrail_questions in case it's not in the form
    const guardrailInput = document.getElementById("guardrail_questions");
    if (guardrailInput) {
      formData.append("guardrail_questions", guardrailInput.value);
    }

    fetch("/analyze", {
      method: "POST",
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Error during analysis.");
      }
      return response.text();
    })
    .then(html => {
      stopProgressUpdates();
      setFormDisabled(analyzeForm, false);
      resultsSection.innerHTML = html;
    })
    .catch(error => {
      console.error("Error during analysis:", error);
      stopProgressUpdates();
      setFormDisabled(analyzeForm, false);
      resultsSection.innerHTML = "<p style='color:red;'>An error occurred. Please try again.</p>";
    });
  });
});