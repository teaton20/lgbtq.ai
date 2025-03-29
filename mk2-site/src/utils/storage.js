export function getItem(key) {
  try {
    return JSON.parse(localStorage.getItem(key));
  } catch (e) {
    console.error("Error reading from localStorage", e);
    return null;
  }
}

export function setItem(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.error("Error writing to localStorage", e);
  }
}
