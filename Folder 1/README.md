# Feedback Dashboard (Folder 1)

This is a small Vite + React scaffold containing a Feedback Analysis Dashboard.

What it includes:
- `src/Dashboard.jsx` - React dashboard component that fetches:
  - `/api/sentiment-counts` -> { positive, negative, neutral }
  - `/api/summarized-feedbacks` -> [ { text, sentiment }, ... ]
  - `/api/wordcloud` -> { url } or { base64 }
- `react-chartjs-2` + `chart.js` for the pie chart
- `axios` for HTTP requests

Quick start

1. Open a terminal in `Folder 1`:

```powershell
cd "c:\Users\Loshini\hackathon\Folder 1"
```

2. Install dependencies:

```powershell
npm install
```

3. Run the dev server:

```powershell
npm run dev
```

Notes
- Replace the API endpoints in `src/Dashboard.jsx` if your backend uses different routes or requires authentication.
- The word cloud endpoint can return `url` or `base64` data; the component handles both.
