import CategoryChart from "./components/CategoryChart";
import SourceChart from "./components/SourceChart";
import CityChart from "./components/CityChart";
import "./App.css";

function App() {
  return (
    <div className="container">
      <h1 className="title">📊 Business Dashboard</h1>

      <div className="grid">
        <div className="card">
          <CityChart />
        </div>

        <div className="card">
          <CategoryChart />
        </div>

        <div className="card">
          <SourceChart />
        </div>
      </div>
    </div>
  );
}

export default App;