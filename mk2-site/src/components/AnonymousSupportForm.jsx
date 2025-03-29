import React, { useState } from 'react';
import { sendSupportRequest } from '../utils/api';

function AnonymousSupportForm() {
  const [formData, setFormData] = useState({ type: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await sendSupportRequest(formData);
    setSubmitted(true);
  };

  if (submitted) {
    return <div>Thank you for your submission!</div>;
  }

  return (
    <form className="support-form" onSubmit={handleSubmit}>
      <label>
        Type:
        <select name="type" value={formData.type} onChange={handleChange}>
          <option value="">Select Type</option>
          <option value="bug">Bug Report</option>
          <option value="feedback">Feedback</option>
          <option value="help">Request Help</option>
        </select>
      </label>
      <label>
        Message:
        <textarea
          name="message"
          value={formData.message}
          onChange={handleChange}
        />
      </label>
      <button type="submit">Submit</button>
    </form>
  );
}

export default AnonymousSupportForm;
