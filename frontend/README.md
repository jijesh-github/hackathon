# Government Amendment Feedback System - Frontend

🏛️ **Professional React + TailwindCSS Frontend for Government Amendment Collection**

A modern, government-style web interface built with React, TailwindCSS, and Lucide icons that provides a professional user experience similar to official government websites like the MCA portal.

## 🎨 Design Features

### Professional Government UI
- ✅ **Clean, official government aesthetic** with blue and white color scheme
- ✅ **Modern typography** using Inter font family
- ✅ **Responsive design** that works on desktop and mobile
- ✅ **Professional navigation** with hover effects and active states
- ✅ **Card-based layouts** with subtle shadows and rounded corners

### User Experience
- 🏠 **Welcome Home Page** with hero section and feature highlights
- 📄 **Amendments Browser** with search, filter, and grid layout
- 💬 **Feedback Submission** with real-time AI analysis display
- 👨‍💼 **Admin Dashboard** for creating and managing amendments

## 🚀 Tech Stack

- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icon library

## 📱 Pages & Features

### 1. Home Page (`/`)
- Professional hero section with government branding
- Feature cards explaining the system
- Statistics display and call-to-action buttons

### 2. Amendments Page (`/amendments`)
- Grid layout with search and category filtering
- Amendment cards with hover effects
- Publication date display

### 3. Feedback Page (`/feedback`)
- Amendment selection dropdown
- AI sentiment analysis display
- Real-time confidence scoring

### 4. Admin Page (`/admin`)
- Professional amendment creation form
- Publishing guidelines sidebar
- Success/error messaging

## 🔧 Development

```bash
npm install          # Install dependencies
npm run dev         # Start development server (http://localhost:5173)
npm run build       # Build for production
```

## 🌐 API Integration

Connects to FastAPI backend at `http://localhost:8000` for:
- Amendment management
- Feedback submission with AI analysis
- Real-time data synchronization

**Live URLs:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
