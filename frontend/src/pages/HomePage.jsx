import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, MessageSquare, Shield, ArrowRight, Users, Gavel } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen" style={{background: 'linear-gradient(to bottom, #f8fafc, white)'}}>
      {/* Hero Section */}
      <div className="bg-primary-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-6">
              Government Amendment
              <span className="block" style={{color: '#bfdbfe'}}>Feedback System</span>
            </h1>
            <p className="text-xl mb-8 mx-auto" style={{color: '#dbeafe', maxWidth: '768px'}}>
              Empowering citizens to participate in democratic governance through 
              transparent feedback on government amendments and policy changes.
            </p>
            <div className="flex justify-center space-x-4">
              <Link to="/amendments" className="btn-primary" style={{backgroundColor: 'white', color: '#2563eb'}}>
                View Amendments
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
              <Link to="/feedback" className="btn-secondary" style={{backgroundColor: '#1d4ed8', color: 'white'}}>
                Submit Feedback
                <MessageSquare className="ml-2 w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4" style={{color: '#1e293b'}}>
              How It Works
            </h2>
            <p className="text-xl mx-auto" style={{color: '#475569', maxWidth: '672px'}}>
              Our AI-powered platform makes it easy to participate in the democratic process
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card text-center">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-government-800 mb-4">
                Browse Amendments
              </h3>
              <p className="text-government-600 mb-6">
                Explore current and proposed amendments with detailed descriptions, 
                categories, and publication dates.
              </p>
              <Link to="/amendments" className="text-primary-600 hover:text-primary-700 font-medium">
                View All Amendments →
              </Link>
            </div>

            {/* Feature 2 */}
            <div className="card text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <MessageSquare className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-government-800 mb-4">
                Submit Feedback
              </h3>
              <p className="text-government-600 mb-6">
                Share your thoughts and opinions on amendments. Our AI analyzes 
                sentiment and provides instant summaries.
              </p>
              <Link to="/feedback" className="text-primary-600 hover:text-primary-700 font-medium">
                Give Feedback →
              </Link>
            </div>

            {/* Feature 3 */}
            <div className="card text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                <Gavel className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-government-800 mb-4">
                AI Analysis
              </h3>
              <p className="text-government-600 mb-6">
                Advanced machine learning provides real-time sentiment analysis 
                and intelligent summarization of public feedback.
              </p>
              <div className="text-primary-600 font-medium">
                Powered by AI →
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-government-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-primary-600 mb-2">500+</div>
              <div className="text-government-600">Amendments Reviewed</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600 mb-2">10K+</div>
              <div className="text-government-600">Citizen Feedback</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600 mb-2">95%</div>
              <div className="text-government-600">Accuracy Rate</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600 mb-2">24/7</div>
              <div className="text-government-600">System Availability</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <Users className="h-16 w-16 text-primary-600 mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-bold text-government-800 mb-6">
            Your Voice Matters
          </h2>
          <p className="text-xl text-government-600 mb-8">
            Join thousands of citizens contributing to better governance. 
            Every feedback helps shape policies that affect our daily lives.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/amendments" className="btn-primary">
              Start Reviewing Amendments
            </Link>
            <Link to="/admin" className="btn-secondary">
              Admin Access
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;