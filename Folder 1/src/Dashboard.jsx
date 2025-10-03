import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Colors,
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend, Colors)

export default function Dashboard() {
  const [counts, setCounts] = useState(null)
  const [summaries, setSummaries] = useState([])
  const [wordCloud, setWordCloud] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const [countsRes, summariesRes, wordCloudRes] = await Promise.all([
          axios.get('/api/sentiment-counts'),
          axios.get('/api/summarized-feedbacks'),
          axios.get('/api/wordcloud'),
        ])

        setCounts(countsRes.data)
        setSummaries(summariesRes.data)

        // wordCloudRes may return { url: '...', base64: '...' }
        const wc = wordCloudRes.data
        if (wc.url) setWordCloud(wc.url)
        else if (wc.base64) setWordCloud(`data:image/png;base64,${wc.base64}`)
        else setWordCloud(null)
      } catch (e) {
        console.error(e)
        setError('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const pieData = counts
    ? {
        labels: ['Positive', 'Negative', 'Neutral'],
        datasets: [
          {
            data: [counts.positive || 0, counts.negative || 0, counts.neutral || 0],
            backgroundColor: ['#16a34a', '#dc2626', '#6b7280'],
          },
        ],
      }
    : null

  return (
    <div className="dashboard-container">
      <h1>Feedback Analysis Dashboard</h1>

      <div className="cards">
        <div className="card chart-card">
          <h2>Sentiment Summary</h2>
          {loading ? (
            <div className="loading">Loading chart...</div>
          ) : error ? (
            <div className="error">{error}</div>
          ) : pieData ? (
            <Pie data={pieData} />
          ) : (
            <div>No data</div>
          )}
        </div>

        <div className="card list-card">
          <h2>Summarized Feedbacks</h2>
          {loading ? (
            <div className="loading">Loading feedbacks...</div>
          ) : summaries && summaries.length > 0 ? (
            <div className="table-scroll">
              <table className="feedback-table">
                <thead>
                  <tr>
                    <th>Summary</th>
                    <th>Sentiment</th>
                  </tr>
                </thead>
                <tbody>
                  {summaries.map((s, i) => (
                    <tr key={i}>
                      <td>{s.text}</td>
                      <td className={`sentiment ${s.sentiment?.toLowerCase()}`}>
                        {s.sentiment}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div>No summaries</div>
          )}
        </div>

        <div className="card wordcloud-card">
          <h2>Word Cloud</h2>
          {loading ? (
            <div className="loading">Loading word cloud...</div>
          ) : wordCloud ? (
            <img src={wordCloud} alt="Word Cloud" className="wordcloud-img" />
          ) : (
            <div>No word cloud available</div>
          )}
        </div>
      </div>
    </div>
  )
}
