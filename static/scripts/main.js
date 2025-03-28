document.addEventListener('DOMContentLoaded', () => {
  const goButton = document.getElementById('goButton');
  const title = document.querySelector('.title');
  const landingView = document.querySelector('.landing-view');
  const resultsSection = document.getElementById('resultsSection');

  // Ensure elements exist before adding events
  if (goButton && title && landingView && resultsSection) {
    goButton.addEventListener('click', () => {
      title.classList.add('vertical');
      landingView.classList.add('moved');
      resultsSection.classList.add('visible');
    });
  }
});