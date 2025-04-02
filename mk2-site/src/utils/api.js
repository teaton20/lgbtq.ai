export async function sendSupportRequest(formData) {
  try {
    const response = await fetch('/api/support', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    return response.json();
  } catch (error) {
    console.error("Error sending support request", error);
  }
}

export async function sendChatMessage(message) {
  try {
    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    return response.json();
  } catch (error) {
    console.error("Error sending chat message", error);
    return { error };
  }
}