import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

function SourceChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/source-count")
      .then(res => setData(res.data));
  }, []);

  return (
    <div>
      <h3>Source-wise Count</h3>

      <BarChart width={400} height={250} data={data}>
        <XAxis dataKey="source" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#2196F3" />  
      </BarChart>
    </div>
  );
}

export default SourceChart;