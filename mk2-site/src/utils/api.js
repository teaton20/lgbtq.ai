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
