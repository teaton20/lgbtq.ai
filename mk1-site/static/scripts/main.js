document.addEventListener('DOMContentLoaded', () => {
  const goButton = document.getElementById('goButton');
  const title = document.querySelector('.title');
  const landingView = document.querySelector('.landing-view');
  const resultsSection = document.getElementById('resultsSection');
  const container = document.querySelector('.container');
  const userInput = document.getElementById('userInput');

  /**
   * Animate UI elements:
   * - Rotates the title vertically.
   * - Reveals the results section.
   * - Repositions the landing view below the results.
   */
  function animateUI() {
    if (title) title.classList.add('vertical');
    if (resultsSection) resultsSection.classList.add('visible');

    // Delay repositioning until the results section transition is complete
    setTimeout(() => {
      if (container && resultsSection && landingView) {
        const containerRect = container.getBoundingClientRect();
        const resultsRect = resultsSection.getBoundingClientRect();
        const newTop = resultsRect.bottom - containerRect.top + 20;
        landingView.style.position = 'absolute';
        landingView.style.top = `${newTop}px`;
        landingView.style.left = '50%';
        landingView.style.transform = 'translateX(-50%)';
      }
    }, 600);
  }

  // Trigger animation on button click
  if (goButton) {
    goButton.addEventListener('click', animateUI);
  }

  // Allow the "Enter" key to trigger the animation from the text input
  if (userInput) {
    userInput.addEventListener('keypress', (event) => {
      if (event.key === 'Enter') {
        animateUI();
      }
    });
  }
});