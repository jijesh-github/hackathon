import React, { useState, useEffect } from 'react';
import { Search, Filter, Calendar, FileText, ArrowRight } from 'lucide-react';
import { apiService } from '../services/api.js';

const AmendmentsPage = () => {
  const [amendments, setAmendments] = useState([]);
  const [filteredAmendments, setFilteredAmendments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Mock categories - in real app, these would come from the API
  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'corporate', label: 'Corporate Affairs' },
    { value: 'taxation', label: 'Taxation' },
    { value: 'compliance', label: 'Compliance' },
    { value: 'digital', label: 'Digital Policy' },
    { value: 'privacy', label: 'Privacy & Data' },
  ];

  useEffect(() => {
    fetchAmendments();
  }, []);

  useEffect(() => {
    filterAmendments();
  }, [amendments, searchTerm, selectedCategory]);

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

  const filterAmendments = () => {
    let filtered = [...amendments];

    // Filter by search term
    if (searchTerm.trim()) {
      filtered = filtered.filter(
        amendment =>
          amendment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          amendment.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category (mock implementation)
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(
        amendment =>
          amendment.title.toLowerCase().includes(selectedCategory.toLowerCase()) ||
          amendment.description.toLowerCase().includes(selectedCategory.toLowerCase())
      );
    }

    setFilteredAmendments(filtered);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const truncateDescription = (text, maxLength = 200) => {
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-government-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-government-600">Loading amendments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-government-50">
      {/* Header */}
      <div className="bg-white border-b border-government-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-government-800 mb-4">
              Government Amendments
            </h1>
            <p className="text-xl text-government-600 max-w-2xl mx-auto">
              Browse and review current and proposed amendments. Click on any amendment 
              to view details and submit your feedback.
            </p>
          </div>

          {/* Search and Filter */}
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search Bar */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-government-400" />
              <input
                type="text"
                placeholder="Search amendments by title or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-10"
              />
            </div>

            {/* Category Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-government-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="form-input pl-10 pr-8 min-w-48"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Results count */}
          <div className="mt-4 text-government-600">
            Showing {filteredAmendments.length} of {amendments.length} amendments
          </div>
        </div>
      </div>

      {/* Amendments Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="text-red-600">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-1 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {filteredAmendments.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-government-300 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-government-600 mb-2">
              No amendments found
            </h3>
            <p className="text-government-500">
              {searchTerm || selectedCategory !== 'all'
                ? 'Try adjusting your search or filter criteria.'
                : 'No amendments are currently available.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAmendments.map((amendment) => (
              <div key={amendment.id} className="card group cursor-pointer">
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-primary-100 p-2 rounded-lg">
                    <FileText className="h-6 w-6 text-primary-600" />
                  </div>
                  <div className="flex items-center text-government-500 text-sm">
                    <Calendar className="h-4 w-4 mr-1" />
                    {formatDate(amendment.created_at)}
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-government-800 mb-3 group-hover:text-primary-600 transition-colors duration-200">
                  {amendment.title}
                </h3>

                <p className="text-government-600 mb-4 text-sm leading-relaxed">
                  {truncateDescription(amendment.description)}
                </p>

                <div className="flex items-center justify-between pt-4 border-t border-government-100">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    Amendment #{amendment.id}
                  </span>
                  
                  <button className="text-primary-600 hover:text-primary-700 font-medium text-sm flex items-center group">
                    View Details
                    <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform duration-200" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AmendmentsPage;