import React, { useState } from 'react';
import { Shield, Plus, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api.js';

const AdminPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.description.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);
      
      const response = await apiService.createAmendment({
        title: formData.title.trim(),
        description: formData.description.trim(),
      });

      if (response.success) {
        setSuccess(`Amendment "${formData.title}" has been created successfully!`);
        setFormData({ title: '', description: '' });
      } else {
        setError(response.message || 'Failed to create amendment.');
      }
    } catch (err) {
      setError('Failed to create amendment. Please try again later.');
      console.error('Error creating amendment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="min-h-screen bg-government-50">
      {/* Header */}
      <div className="bg-white border-b border-government-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="bg-primary-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-government-800 mb-4">
              Admin Dashboard
            </h1>
            <p className="text-xl text-government-600 max-w-2xl mx-auto">
              Create and manage government amendments. Published amendments will be 
              available for public review and feedback collection.
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="flex items-center mb-6">
                <Plus className="h-6 w-6 text-primary-600 mr-3" />
                <h2 className="text-xl font-semibold text-government-800">
                  Create New Amendment
                </h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Title Field */}
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-government-700 mb-2">
                    Amendment Title *
                  </label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="Enter a clear and descriptive title for the amendment"
                    className="form-input"
                    maxLength={500}
                    required
                  />
                  <div className="text-right text-sm text-government-500 mt-1">
                    {formData.title.length}/500 characters
                  </div>
                </div>

                {/* Description Field */}
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-government-700 mb-2">
                    Amendment Description *
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={12}
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Provide a comprehensive description of the amendment, including its purpose, scope, and expected impact. Include relevant sections, clauses, and implementation details."
                    className="form-input resize-none"
                    required
                  />
                  <div className="text-right text-sm text-government-500 mt-1">
                    {formData.description.length} characters
                  </div>
                </div>

                {/* Success Message */}
                {success && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
                    <div className="text-green-700 text-sm">{success}</div>
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
                    <div className="text-red-700 text-sm">{error}</div>
                  </div>
                )}

                {/* Submit Button */}
                <div className="flex justify-end space-x-4">
                  <button
                    type="button"
                    onClick={() => setFormData({ title: '', description: '' })}
                    className="btn-secondary"
                    disabled={submitting}
                  >
                    Clear Form
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || !formData.title.trim() || !formData.description.trim()}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {submitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Publishing...
                      </>
                    ) : (
                      <>
                        Publish Amendment
                        <Plus className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Information Panel */}
          <div className="space-y-6">
            {/* Guidelines */}
            <div className="card">
              <h3 className="text-lg font-semibold text-government-800 mb-4">
                Publishing Guidelines
              </h3>
              <ul className="space-y-2 text-sm text-government-600">
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Use clear, descriptive titles
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Include complete amendment text
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Specify implementation timeline
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Reference relevant acts and sections
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Include contact information for queries
                </li>
              </ul>
            </div>

            {/* Process Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-government-800 mb-4">
                Amendment Process
              </h3>
              <div className="space-y-3 text-sm text-government-600">
                <div className="flex items-start">
                  <div className="bg-blue-100 w-6 h-6 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                    <span className="text-blue-600 text-xs font-medium">1</span>
                  </div>
                  <div>
                    <div className="font-medium text-government-700">Draft & Publish</div>
                    <div>Create amendment and make it available for public review</div>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="bg-green-100 w-6 h-6 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                    <span className="text-green-600 text-xs font-medium">2</span>
                  </div>
                  <div>
                    <div className="font-medium text-government-700">Collect Feedback</div>
                    <div>Citizens and stakeholders submit their opinions</div>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="bg-purple-100 w-6 h-6 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                    <span className="text-purple-600 text-xs font-medium">3</span>
                  </div>
                  <div>
                    <div className="font-medium text-government-700">AI Analysis</div>
                    <div>Automated sentiment analysis and summarization</div>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="bg-orange-100 w-6 h-6 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                    <span className="text-orange-600 text-xs font-medium">4</span>
                  </div>
                  <div>
                    <div className="font-medium text-government-700">Review & Decide</div>
                    <div>Analyze feedback for final policy decisions</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Security Notice */}
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
              <div className="flex items-start">
                <Shield className="h-5 w-5 text-primary-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-primary-800 mb-1">
                    Security Notice
                  </h4>
                  <p className="text-sm text-primary-700">
                    All amendments are logged with timestamps and user information. 
                    Ensure content accuracy before publishing as amendments become 
                    publicly visible immediately.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;