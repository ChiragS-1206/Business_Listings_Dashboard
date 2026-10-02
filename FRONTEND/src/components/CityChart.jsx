import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

function CityChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/city-count")
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h3>City-wise Business Count</h3>

      <BarChart width={400} height={250} data={data}>
        <XAxis dataKey="city" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#4CAF50" />   
      </BarChart>
    </div>
  );
}

export default CityChart;