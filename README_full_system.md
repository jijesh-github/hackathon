# Government Amendment Feedback System

🏛️ **AI-Powered Feedback Collection System for Government Amendments**

A comprehensive web application that allows government officials to post amendments and collect public feedback with real-time AI analysis using DistilBERT and BART models.

## 🚀 Features

### For Government Officials (Admin)
- ✅ Create and publish new amendments
- ✅ View all published amendments
- ✅ Access feedback analytics and sentiment analysis

### For Public/Stakeholders
- ✅ Browse available amendments
- ✅ Submit detailed feedback
- ✅ Real-time AI analysis of submissions
- ✅ Instant sentiment and summary results

### AI & Analytics
- 🤖 **Real Sentiment Analysis** using DistilBERT model
- 📝 **Text Summarization** using BART model with 15-word rule
- ☁️ **Word Cloud Generation** for visual feedback analysis
- 📊 **Confidence Scoring** for sentiment predictions

### Database & API
- 🗄️ **SQLite/PostgreSQL** database with Alembic migrations
- 🔗 **RESTful API** endpoints for all operations
- 📱 **CORS enabled** for frontend integration
- 🔒 **Data persistence** and relationship management

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (Database ORM)
- Alembic (Database migrations)
- Transformers (HuggingFace)
- DistilBERT (Sentiment analysis)
- BART (Text summarization)
- WordCloud (Visualization)

**Database:**
- SQLite (Development)
- PostgreSQL (Production - Neon)

**Frontend:**
- HTML5 + JavaScript (Vanilla)
- CSS3 (Responsive design)
- Fetch API (HTTP requests)

## 📋 Database Schema

### Amendments Table
```sql
- id (Primary Key)
- title (String, max 500 chars)
- description (Text)
- created_at (Timestamp)
```

### Feedback Table
```sql
- id (Primary Key)
- amendment_id (Foreign Key → amendments.id)
- original_text (Text, max 5000 chars)
- summary (Text, AI-generated)
- sentiment (String: positive/negative/neutral)
- sentiment_confidence (Float: 0.0-1.0)
- created_at (Timestamp)
```

## 🗂️ Project Structure

```
backend/
├── app_full_system.py          # Main application server
├── models.py                   # SQLAlchemy database models
├── schemas.py                  # Pydantic validation schemas
├── test_full_system.py         # System testing script
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic configuration
├── alembic.ini                 # Alembic settings
└── feedback_system.db          # SQLite database (dev)

root/
└── .env                        # Environment variables
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv alembic transformers torch wordcloud matplotlib pandas
```

### 2. Setup Environment
```bash
# Copy .env.example to .env and configure
DATABASE_URL=sqlite:///./feedback_system.db  # For development
# DATABASE_URL=postgresql+psycopg2://user:pass@host/db  # For production
```

### 3. Initialize Database
```bash
cd backend
alembic upgrade head
```

### 4. Test System
```bash
python test_full_system.py
```

### 5. Start Server
```bash
python app_full_system.py
```

### 6. Access Application
- **Web Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **System Info:** http://localhost:8000/info

## 📡 API Endpoints

### Amendments
- `POST /amendments` - Create new amendment
- `GET /amendments` - List all amendments

### Feedback
- `POST /feedback` - Submit feedback (with AI analysis)
- `GET /feedback/{amendment_id}` - Get feedback for amendment

### Legacy
- `POST /analyze` - Analyze CSV files (backwards compatibility)

### System
- `GET /` - Web interface
- `GET /info` - System information

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_full_system.py
```

Tests cover:
- ✅ Database connectivity and operations
- ✅ ML model loading and analysis
- ✅ API endpoint functionality
- ✅ Data validation and persistence

## 🗄️ Database Migration

### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database (choose one)
DATABASE_URL=sqlite:///./feedback_system.db                                    # Development
DATABASE_URL=postgresql+psycopg2://user:pass@host.neon.tech/db                # Production

# Optional settings
LOG_LEVEL=INFO
DEBUG=true
```

### Production Deployment (Neon PostgreSQL)
1. Create a Neon PostgreSQL database
2. Update `.env` with your Neon connection string:
   ```env
   DATABASE_URL=postgresql+psycopg2://username:password@ep-xxxx.neon.tech/dbname
   ```
3. Run migrations: `alembic upgrade head`
4. Start server with production settings

## 📊 Example Usage

### Creating an Amendment (Admin)
```javascript
const amendment = {
    title: "Digital Privacy Protection Act 2025",
    description: "This amendment establishes comprehensive digital privacy rights..."
};

fetch('/amendments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(amendment)
});
```

### Submitting Feedback (Public)
```javascript
const feedback = {
    amendment_id: 1,
    original_text: "I support this amendment as it will protect our privacy rights..."
};

fetch('/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback)
});
```

## 🎯 Data Flow

1. **Admin creates amendment** → Stored in database
2. **Public submits feedback** → AI analysis → Results stored
3. **System provides real-time analytics** → Dashboard visualization

## 🔮 Future Enhancements

- 👥 User authentication and role management
- 📈 Advanced analytics dashboard
- 🔔 Email notifications for new amendments
- 🌐 Multi-language support
- 📱 Mobile app development
- 🤖 Enhanced AI models for policy-specific analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_full_system.py`
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- **Issues:** GitHub Issues
- **Documentation:** API docs at `/docs`
- **Testing:** Run `test_full_system.py`

---

🎉 **Ready to collect and analyze government amendment feedback with AI!**