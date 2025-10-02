const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  async request(url, options = {}) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Amendment APIs
  async getAmendments() {
    return this.request('/amendments');
  }

  async createAmendment(amendment) {
    return this.request('/amendments', {
      method: 'POST',
      body: JSON.stringify(amendment),
    });
  }

  // Feedback APIs
  async submitFeedback(feedback) {
    return this.request('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  async getFeedbackByAmendment(amendmentId) {
    return this.request(`/feedback/${amendmentId}`);
  }
}

export const apiService = new ApiService();