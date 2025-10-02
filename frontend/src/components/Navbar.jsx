import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, MessageSquare, Shield, Home } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-lg border-b" style={{borderColor: '#e2e8f0'}}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand */}
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{color: '#1e293b'}}>
                Government Amendment System
              </h1>
              <p className="text-sm" style={{color: '#64748b'}}>
                Ministry of Corporate Affairs
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/"
              className={isActive('/') ? 'navbar-link-active' : 'navbar-link'}
            >
              <div className="flex items-center space-x-2">
                <Home className="h-4 w-4" />
                <span>Home</span>
              </div>
            </Link>

            <Link
              to="/amendments"
              className={isActive('/amendments') ? 'navbar-link-active' : 'navbar-link'}
            >
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Amendments</span>
              </div>
            </Link>

            <Link
              to="/feedback"
              className={isActive('/feedback') ? 'navbar-link-active' : 'navbar-link'}
            >
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-4 w-4" />
                <span>Feedback</span>
              </div>
            </Link>

            <Link
              to="/admin"
              className={isActive('/admin') ? 'navbar-link-active' : 'navbar-link'}
            >
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4" />
                <span>Admin</span>
              </div>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="text-government-600 hover:text-primary-600 p-2">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;