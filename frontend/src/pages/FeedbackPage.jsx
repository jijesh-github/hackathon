import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, CheckCircle, AlertCircle, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import { apiService } from '../services/api.js';

const FeedbackPage = () => {
  const [amendments, setAmendments] = useState([]);
  const [selectedAmendment, setSelectedAmendment] = useState('');
  const [feedbackText, setFeedbackText] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAmendments();
  }, []);

  const fetchAmendments = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAmendments();
      setAmendments(response.amendments);
    } catch (err) {
      setError('Failed to fetch amendments. Please try again later.');
      console.error('Error fetching amendments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedAmendment || !feedbackText.trim()) {
      setError('Please select an amendment and enter your feedback.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      const response = await apiService.submitFeedback({
        amendment_id: parseInt(selectedAmendment),
        original_text: feedbackText.trim(),
      });

      if (response.success) {
        // Non-toxic content processed successfully
        setResult(response.data);
        setFeedbackText('');
        setSelectedAmendment('');
      } else {
        // Check if it's a toxicity issue
        if (response.data && response.data.toxic) {
          setError(`🚫 ${response.message} (Toxicity Score: ${(response.data.toxic_score * 100).toFixed(1)}%)`);
        } else {
          setError(response.message || 'Failed to submit feedback.');
        }
      }
    } catch (err) {
      setError('Failed to submit feedback. Please try again later.');
      console.error('Error submitting feedback:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const getSelectedAmendmentDetails = () => {
    if (!selectedAmendment) return null;
    return amendments.find(a => a.id.toString() === selectedAmendment);
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <ThumbsUp className="h-5 w-5 text-green-600" />;
      case 'negative':
        return <ThumbsDown className="h-5 w-5 text-red-600" />;
      default:
        return <Minus className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'negative':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    }
  };

  return (
    <div className="min-h-screen bg-government-50">
      {/* Header */}
      <div className="bg-white border-b border-government-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageSquare className="h-8 w-8 text-primary-600" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-government-800 mb-4">
              Submit Feedback
            </h1>
            <p className="text-xl text-government-600 max-w-2xl mx-auto">
              Share your thoughts on government amendments. Our AI will analyze 
              your feedback and provide instant insights on sentiment and key points.
            </p>
          </div>
        </div>
      </div>

      {/* Feedback Form */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <div className="card">
              <h2 className="text-xl font-semibold text-government-800 mb-6">
                Provide Your Feedback
              </h2>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Amendment Selection */}
                <div>
                  <label htmlFor="amendment" className="block text-sm font-medium text-government-700 mb-2">
                    Select Amendment *
                  </label>
                  <select
                    id="amendment"
                    value={selectedAmendment}
                    onChange={(e) => setSelectedAmendment(e.target.value)}
                    className="form-input"
                    disabled={loading}
                    required
                  >
                    <option value="">
                      {loading ? 'Loading amendments...' : 'Choose an amendment to provide feedback on'}
                    </option>
                    {amendments.map((amendment) => (
                      <option key={amendment.id} value={amendment.id}>
                        {amendment.title}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Amendment Preview */}
                {getSelectedAmendmentDetails() && (
                  <div className="bg-government-50 rounded-lg p-4 border border-government-200">
                    <h3 className="font-medium text-government-800 mb-2">
                      Selected Amendment:
                    </h3>
                    <p className="text-sm text-government-600 mb-2">
                      {getSelectedAmendmentDetails()?.title}
                    </p>
                    <p className="text-xs text-government-500">
                      {getSelectedAmendmentDetails()?.description.substring(0, 200)}...
                    </p>
                  </div>
                )}

                {/* Feedback Text */}
                <div>
                  <label htmlFor="feedback" className="block text-sm font-medium text-government-700 mb-2">
                    Your Feedback *
                  </label>
                  <textarea
                    id="feedback"
                    rows={8}
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    placeholder="Share your detailed thoughts, concerns, or suggestions about this amendment. Be specific about how it might impact you or your organization..."
                    className="form-input resize-none"
                    maxLength={5000}
                    required
                  />
                  <div className="text-right text-sm text-government-500 mt-1">
                    {feedbackText.length}/5000 characters
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
                    <div className="text-red-700 text-sm">{error}</div>
                  </div>
                )}

                {/* Submit Button */}
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={submitting || !selectedAmendment || !feedbackText.trim()}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {submitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        Submit Feedback
                        <Send className="ml-2 h-4 w-4" />
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
                Feedback Guidelines
              </h3>
              <ul className="space-y-2 text-sm text-government-600">
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Be specific and constructive in your feedback
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Focus on the amendment's impact and implications
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Provide evidence or examples when possible
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  Maintain respectful and professional language
                </li>
              </ul>
            </div>

            {/* AI Analysis Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-government-800 mb-4">
                AI Analysis Features
              </h3>
              <div className="space-y-3 text-sm text-government-600">
                <div className="flex items-center">
                  <div className="bg-blue-100 p-1 rounded mr-3">
                    <MessageSquare className="h-4 w-4 text-blue-600" />
                  </div>
                  <span>Sentiment Analysis</span>
                </div>
                <div className="flex items-center">
                  <div className="bg-green-100 p-1 rounded mr-3">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  </div>
                  <span>Automatic Summarization</span>
                </div>
                <div className="flex items-center">
                  <div className="bg-purple-100 p-1 rounded mr-3">
                    <AlertCircle className="h-4 w-4 text-purple-600" />
                  </div>
                  <span>Confidence Scoring</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Result */}
        {result && (
          <div className="mt-8 card">
            <div className="flex items-center mb-6">
              <CheckCircle className="h-6 w-6 text-green-600 mr-3" />
              <h3 className="text-xl font-semibold text-government-800">
                Feedback Submitted Successfully!
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Sentiment Analysis */}
              <div>
                <h4 className="text-lg font-medium text-government-800 mb-3">
                  Sentiment Analysis
                </h4>
                <div className={`border rounded-lg p-4 ${getSentimentColor(result.sentiment)}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {getSentimentIcon(result.sentiment)}
                      <span className="ml-2 font-medium capitalize">
                        {result.sentiment}
                      </span>
                    </div>
                    <span className="text-sm font-medium">
                      {(result.confidence * 100).toFixed(1)}% confidence
                    </span>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div>
                <h4 className="text-lg font-medium text-government-800 mb-3">
                  AI Summary
                </h4>
                <div className="bg-government-50 border border-government-200 rounded-lg p-4">
                  <p className="text-government-700 italic">
                    "{result.summary}"
                  </p>
                </div>
              </div>
            </div>

            {/* Safety Check Info */}
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center text-green-800">
                <CheckCircle className="h-4 w-4 mr-2" />
                <span className="font-medium">Content Safety Verified</span>
              </div>
              <p className="text-sm text-green-700 mt-1">
                Your feedback passed our toxicity screening (Safety Score: {((1 - result.toxic_score) * 100).toFixed(1)}%) and has been processed successfully.
              </p>
            </div>

            <div className="mt-4 text-sm text-government-500">
              Your feedback has been recorded and will contribute to the analysis dashboard. 
              Thank you for participating in the democratic process!
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackPage;