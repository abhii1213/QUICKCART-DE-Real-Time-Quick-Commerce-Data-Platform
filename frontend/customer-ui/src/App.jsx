import { useState } from "react";
import "./App.css";
import { api } from "./services/api";
import { buildEvent } from "./utils/eventBuilder";

const mockProducts = [
  { product_id: "P101", name: "Milk", price: 52 },
  { product_id: "P102", name: "Bread", price: 35 },
  { product_id: "P103", name: "Eggs", price: 80 },
  { product_id: "P104", name: "Rice", price: 65 },
];

function App() {
  const [logs, setLogs] = useState([]);
  const [cart, setCart] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [orderDetails, setOrderDetails] = useState({
    name: "",
    phone: "",
    city: "",
    area: "",
  });

  const logEvent = (event) => {
    setLogs((prev) => [JSON.stringify(event, null, 2), ...prev]);
  };

  const sendEvent = async (endpoint, event) => {
    try {
      await api.post(endpoint, event);
      logEvent(event);
    } catch {
      logEvent({
        error: "FastAPI endpoint not ready yet",
        event,
      });
    }
  };

  const handleViewProduct = (product) => {
    const event = buildEvent("PRODUCT_VIEWED", "customer-ui", {
      user_id: "U101",
      product_id: product.product_id,
    });

    sendEvent("/activity-event", event);
  };

  const handleSearch = () => {
    const event = buildEvent("PRODUCT_SEARCHED", "customer-ui", {
      user_id: "U101",
      search_text: searchText,
    });

    sendEvent("/activity-event", event);
  };

  const handleAddToCart = (product) => {
    setCart([...cart, product]);

    const event = buildEvent("ADD_TO_CART", "customer-ui", {
      user_id: "U101",
      product_id: product.product_id,
      qty: 1,
    });

    sendEvent("/cart-event", event);
  };

  const handleRemoveFromCart = (product) => {
    setCart(cart.filter((item) => item.product_id !== product.product_id));

    const event = buildEvent("REMOVE_FROM_CART", "customer-ui", {
      user_id: "U101",
      product_id: product.product_id,
    });

    sendEvent("/cart-event", event);
  };

  const handleCheckout = () => {
    const event = buildEvent("CHECKOUT_STARTED", "customer-ui", {
      user_id: "U101",
    });

    sendEvent("/activity-event", event);
  };

  const handlePlaceOrder = () => {
    const total = cart.reduce((sum, item) => sum + item.price, 0);

    const event = buildEvent("ORDER_PLACED", "customer-ui", {
      order_id: crypto.randomUUID(),
      user: {
        user_id: "U101",
        ...orderDetails,
      },
      payment_mode: "COD",
      items: cart.map((item) => ({
        product_id: item.product_id,
        product_name: item.name,
        qty: 1,
        unit_price: item.price,
      })),
      total_amount: total,
    });

    sendEvent("/order-event", event);
  };

  const handleCancelOrder = () => {
    const event = buildEvent("ORDER_CANCELLED", "customer-ui", {
      user_id: "U101",
    });

    sendEvent("/order-event", event);
  };

  return (
    <div className="container">
      <h1>QuickCart Customer Dashboard</h1>

      <div className="search-box">
        <input
          placeholder="Search products"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      <section className="card">
        <h2>Products</h2>
        {mockProducts.map((product) => (
          <div key={product.product_id} className="product-row">
            <span>
              {product.name} - ₹{product.price}
            </span>
            <div>
              <button onClick={() => handleViewProduct(product)}>View</button>
              <button onClick={() => handleAddToCart(product)}>Add</button>
            </div>
          </div>
        ))}
      </section>

      <section className="card">
        <h2>Cart</h2>
        {cart.map((item) => (
          <div key={item.product_id} className="product-row">
            <span>{item.name}</span>
            <button onClick={() => handleRemoveFromCart(item)}>Remove</button>
          </div>
        ))}
        <button onClick={handleCheckout}>Checkout</button>
      </section>

      <section className="card">
        <h2>Checkout Details</h2>
        <input
          placeholder="Name"
          onChange={(e) =>
            setOrderDetails({ ...orderDetails, name: e.target.value })
          }
        />
        <input
          placeholder="Phone"
          onChange={(e) =>
            setOrderDetails({ ...orderDetails, phone: e.target.value })
          }
        />
        <input
          placeholder="City"
          onChange={(e) =>
            setOrderDetails({ ...orderDetails, city: e.target.value })
          }
        />
        <input
          placeholder="Area"
          onChange={(e) =>
            setOrderDetails({ ...orderDetails, area: e.target.value })
          }
        />

        <button onClick={handlePlaceOrder}>Place COD Order</button>
        <button onClick={handleCancelOrder}>Cancel Order</button>
      </section>

      <div className="console">
        <h2>Event Console</h2>
        {logs.map((log, idx) => (
          <pre key={idx}>{log}</pre>
        ))}
      </div>
    </div>
  );
}

export default App;