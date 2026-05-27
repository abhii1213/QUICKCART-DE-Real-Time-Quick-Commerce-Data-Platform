import { useState } from "react";
import "./App.css";
import { api } from "./services/api";

function App() {
  const [logs, setLogs] = useState([]);

  const [product, setProduct] = useState({
    product_id: "",
    product_name: "",
    category: "",
    price: "",
    stock_qty: "",
  });

  const [priceUpdate, setPriceUpdate] = useState({
    product_id: "",
    price: "",
  });

  const [inventory, setInventory] = useState({
    product_id: "",
    stock_qty: "",
  });

  const [delist, setDelist] = useState({
    product_id: "",
  });

  const logEvent = (data) => {
    setLogs((prev) => [JSON.stringify(data, null, 2), ...prev]);
  };

  const handleCreateProduct = async () => {
    try {
      const res = await api.post("/products", {
        ...product,
        price: Number(product.price),
        stock_qty: Number(product.stock_qty),
      });

      logEvent(res.data);
    } catch (err) {
      console.error(err);
      logEvent({
        error: "Create Product Failed",
      });
    }
  };

  const handlePriceUpdate = async () => {
    try {
      const res = await api.put(
        `/products/${priceUpdate.product_id}/price`,
        {
          price: Number(priceUpdate.price),
        }
      );

      logEvent(res.data);
    } catch (err) {
      console.error(err);
      logEvent({
        error: "Price Update Failed",
      });
    }
  };

  const handleInventoryUpdate = async () => {
    try {
      const res = await api.put(
        `/products/${inventory.product_id}/inventory`,
        {
          stock_qty: Number(inventory.stock_qty),
        }
      );

      logEvent(res.data);
    } catch (err) {
      console.error(err);
      logEvent({
        error: "Inventory Update Failed",
      });
    }
  };

  const handleDelist = async () => {
    try {
      const res = await api.delete(
        `/products/${delist.product_id}`
      );

      logEvent(res.data);
    } catch (err) {
      console.error(err);
      logEvent({
        error: "Delist Failed",
      });
    }
  };

  return (
    <div className="container">
      <h1>QuickCart Admin Dashboard</h1>

      <div className="grid">
        <Card title="Create Product">
          <InputFields data={product} setData={setProduct} />
          <button onClick={handleCreateProduct}>
            Create Product
          </button>
        </Card>

        <Card title="Update Price">
          <InputFields
            data={priceUpdate}
            setData={setPriceUpdate}
          />
          <button onClick={handlePriceUpdate}>
            Update Price
          </button>
        </Card>

        <Card title="Update Inventory">
          <InputFields
            data={inventory}
            setData={setInventory}
          />
          <button onClick={handleInventoryUpdate}>
            Update Inventory
          </button>
        </Card>

        <Card title="Delist Product">
          <InputFields data={delist} setData={setDelist} />
          <button onClick={handleDelist}>
            Delist Product
          </button>
        </Card>
      </div>

      <div className="console">
        <h2>Admin Console</h2>
        {logs.map((log, idx) => (
          <pre key={idx}>{log}</pre>
        ))}
      </div>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}

function InputFields({ data, setData }) {
  return (
    <>
      {Object.keys(data).map((key) => (
        <input
          key={key}
          placeholder={key}
          value={data[key]}
          onChange={(e) =>
            setData({
              ...data,
              [key]: e.target.value,
            })
          }
        />
      ))}
    </>
  );
}

export default App;