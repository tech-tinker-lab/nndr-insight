import React, { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Area } from "recharts";

export default function ForecastChart({ category_code, area, agg, periods = 12 }) {
  const [forecast, setForecast] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/forecast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          periods,
          category_code,
          area,
          agg,
        }),
      });
      const json = await res.json();
      setForecast(json.forecast || []);
      setHistory(json.history || []);
    } catch (e) {
      setError("Failed to fetch forecast");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="font-semibold mb-2">Forecast Chart</h2>
      <button className="bg-green-500 text-white px-4 py-2 rounded mb-4" onClick={getForecast} disabled={loading}>
        {loading ? "Loading..." : "Run Forecast"}
      </button>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {(forecast.length > 0 || history.length > 0) && (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart>
            <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
            <XAxis dataKey="ds" type="category" />
            <YAxis />
            <Tooltip />
            {/* Confidence interval area */}
            {forecast.length > 0 && (
              <Area
                dataKey="yhat"
                data={forecast}
                type="monotone"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.1}
                dot={false}
                activeDot={false}
                isAnimationActive={false}
                yAxisId={0}
                baseLine={forecast.map(f => f.yhat_lower)}
              />
            )}
            {/* Forecast line */}
            {forecast.length > 0 && (
              <Line
                type="monotone"
                dataKey="yhat"
                data={forecast}
                stroke="#8884d8"
                dot={false}
                name="Forecast"
              />
            )}
            {/* Lower/upper bounds as lines */}
            {forecast.length > 0 && (
              <Line
                type="monotone"
                dataKey="yhat_lower"
                data={forecast}
                stroke="#bbb"
                dot={false}
                strokeDasharray="3 3"
                name="Lower Bound"
              />
            )}
            {forecast.length > 0 && (
              <Line
                type="monotone"
                dataKey="yhat_upper"
                data={forecast}
                stroke="#bbb"
                dot={false}
                strokeDasharray="3 3"
                name="Upper Bound"
              />
            )}
            {/* Historical data overlay */}
            {history.length > 0 && (
              <Line
                type="monotone"
                dataKey="y"
                data={history}
                stroke="#2ecc40"
                dot={false}
                name="History"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}