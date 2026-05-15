import { useState } from "react";
import "./App.css";
import { api } from "./services/api";
import { buildEvent } from "./utils/eventBuilder";

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
    old_price: "",
    new_price: "",
  });

  const [inventory, setInventory] = useState({
    product_id: "",
    stock_qty: "",
  });

  const [delist, setDelist] = useState({
    product_id: "",
  });

  const [flashSale, setFlashSale] = useState({
    product_id: "",
    discount_percent: "",
  });

  const logEvent = (event) => {
    setLogs((prev) => [JSON.stringify(event, null, 2), ...prev]);
  };

  const sendEvent = async (endpoint, event) => {
    try {
      await api.post(endpoint, event);
      logEvent(event);
    } catch (err) {
      console.error(err);
      logEvent({
        error: "FastAPI endpoint not ready yet",
        event,
      });
    }
  };

  const handleCreateProduct = () => {
    const event = buildEvent("PRODUCT_CREATED", "admin-ui", product);
    sendEvent("/product-event", event);
  };

  const handlePriceUpdate = () => {
    const event = buildEvent("PRICE_UPDATED", "admin-ui", priceUpdate);
    sendEvent("/product-event", event);
  };

  const handleInventoryUpdate = () => {
    const event = buildEvent("INVENTORY_UPDATED", "admin-ui", inventory);
    sendEvent("/inventory-event", event);
  };

  const handleDelist = () => {
    const event = buildEvent("PRODUCT_DELISTED", "admin-ui", delist);
    sendEvent("/product-event", event);
  };

  const handleFlashSale = () => {
    const event = buildEvent("FLASH_SALE_STARTED", "admin-ui", flashSale);
    sendEvent("/product-event", event);
  };

  return (
    <div className="container">
      <h1>QuickCart Admin Dashboard</h1>

      <div className="grid">

        <Card title="Create Product">
          <InputFields data={product} setData={setProduct} />
          <button onClick={handleCreateProduct}>Create Product</button>
        </Card>

        <Card title="Update Price">
          <InputFields data={priceUpdate} setData={setPriceUpdate} />
          <button onClick={handlePriceUpdate}>Update Pricee</button>
        </Card>

        <Card title="Update Inventory">
          <InputFields data={inventory} setData={setInventory} />
          <button onClick={handleInventoryUpdate}>Update Inventory</button>
        </Card>

        <Card title="Delist Product">
          <InputFields data={delist} setData={setDelist} />
          <button onClick={handleDelist}>Delist Product</button>
        </Card>

        <Card title="Flash Sale">
          <InputFields data={flashSale} setData={setFlashSale} />
          <button onClick={handleFlashSale}>Start Flash Sale</button>
        </Card>

      </div>

      <div className="console">
        <h2>Event Console</h2>
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