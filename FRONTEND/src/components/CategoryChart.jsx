import { useEffect, useState } from "react";
import axios from "axios";
import { PieChart, Pie, Tooltip, Cell } from "recharts"; // ✅ Cell added

function CategoryChart() {
  const [data, setData] = useState([]);

  const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7f50", "#00C49F"];

  useEffect(() => {
    axios.get("http://localhost:8000/category-count")
      .then(res => {
        console.log("Category Data:", res.data); // debug
        setData(res.data);
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h3>Category-wise Distribution</h3>

      {data.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <PieChart width={400} height={300}>
          <Pie
            data={data}
            dataKey="count"
            nameKey="category"
            cx="50%"
            cy="50%"
            outerRadius={100}
            label
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      )}
    </div>
  );
}

export default CategoryChart;