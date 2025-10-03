import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Pie } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function DashboardPage() {
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
        setSummaries(summariesRes.data || [])

        const wc = wordCloudRes.data
        if (wc?.url) setWordCloud(wc.url)
        else if (wc?.base64) setWordCloud(`data:image/png;base64,${wc.base64}`)
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
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-6">Feedback Analysis Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-4 lg:col-span-1">
          <h2 className="font-medium mb-2">Sentiment Summary</h2>
          {loading ? (
            <p className="text-gray-500">Loading chart...</p>
          ) : error ? (
            <p className="text-red-600">{error}</p>
          ) : pieData ? (
            <Pie data={pieData} />
          ) : (
            <p>No data</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-4 lg:col-span-1">
          <h2 className="font-medium mb-2">Word Cloud</h2>
          {loading ? (
            <p className="text-gray-500">Loading word cloud...</p>
          ) : wordCloud ? (
            <img src={wordCloud} alt="Word Cloud" className="max-w-full max-h-64 rounded" />
          ) : (
            <p>No word cloud</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-4 lg:col-span-1">
          <h2 className="font-medium mb-2">Summarized Feedbacks</h2>
          {loading ? (
            <p className="text-gray-500">Loading feedbacks...</p>
          ) : summaries && summaries.length > 0 ? (
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {summaries.map((s, i) => (
                <div key={i} className="p-2 border rounded">
                  <p className="text-sm text-gray-700">{s.text}</p>
                  <p className="text-xs font-semibold mt-1 text-gray-500">{s.sentiment}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>No summaries</p>
          )}
        </div>
      </div>
    </div>
  )
}
