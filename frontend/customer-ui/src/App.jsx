import { useEffect, useState } from "react";
import "./App.css";
import { api } from "./services/api";

function App() {
  const [token, setToken] = useState(
    localStorage.getItem("quickcart_token")
  );

  const [authMode, setAuthMode] = useState("login");

  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    city: "",
    area: "",
  });

  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [showCheckout, setShowCheckout] = useState(false);
  const [message, setMessage] = useState("");

  /*
    Fetch product catalog after login
  */
  const fetchProducts = async () => {
    try {
      const res = await api.get("/products");
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (token) {
      fetchProducts();
    }
  }, [token]);

  /*
    Signup
  */
  const handleSignup = async () => {
    try {
      const res = await api.post("/auth/signup", authForm);

      localStorage.setItem(
        "quickcart_token",
        res.data.access_token
      );

      setToken(res.data.access_token);
      setMessage("Signup successful!");
    } catch (err) {
      console.error(err);
      setMessage("Signup failed.");
    }
  };

  /*
    Login
  */
  const handleLogin = async () => {
    try {
      const res = await api.post("/auth/login", {
        email: authForm.email,
        password: authForm.password,
      });

      localStorage.setItem(
        "quickcart_token",
        res.data.access_token
      );

      setToken(res.data.access_token);
      setMessage("Login successful!");
    } catch (err) {
      console.error(err);
      setMessage("Invalid credentials.");
    }
  };

  /*
    Logout
  */
  const handleLogout = () => {
    localStorage.removeItem("quickcart_token");
    setToken(null);
    setProducts([]);
    setCart([]);
    setShowCheckout(false);
  };

  /*
    Add product to cart
  */
  const addToCart = (product) => {
    const existing = cart.find(
      (item) => item.product_id === product.product_id
    );

    if (existing) {
      if (existing.qty >= product.stock_qty) {
        setMessage("Stock limit reached.");
        return;
      }

      setCart(
        cart.map((item) =>
          item.product_id === product.product_id
            ? {
                ...item,
                qty: item.qty + 1,
                line_total: (item.qty + 1) * item.unit_price,
              }
            : item
        )
      );
    } else {
      setCart([
        ...cart,
        {
          product_id: product.product_id,
          product_name: product.product_name,
          unit_price: product.price,
          qty: 1,
          line_total: product.price,
          available_stock: product.stock_qty,
        },
      ]);
    }
  };

  /*
    Increase cart quantity
  */
  const increaseQty = (product_id) => {
    setCart(
      cart.map((item) =>
        item.product_id === product_id
          ? {
              ...item,
              qty: item.qty + 1,
              line_total: (item.qty + 1) * item.unit_price,
            }
          : item
      )
    );
  };

  /*
    Decrease cart quantity
  */
  const decreaseQty = (product_id) => {
    setCart(
      cart
        .map((item) => {
          if (item.product_id === product_id) {
            if (item.qty === 1) return null;

            return {
              ...item,
              qty: item.qty - 1,
              line_total: (item.qty - 1) * item.unit_price,
            };
          }

          return item;
        })
        .filter(Boolean)
    );
  };

  /*
    Remove cart item
  */
  const removeItem = (product_id) => {
    setCart(
      cart.filter(
        (item) => item.product_id !== product_id
      )
    );
  };

  /*
    Cart subtotal
  */
  const cartTotal = cart.reduce(
    (sum, item) => sum + item.line_total,
    0
  );

  /*
    REAL order placement
  */
  const placeOrder = async () => {
    try {
      const payload = {
        items: cart.map((item) => ({
          product_id: item.product_id,
          qty: item.qty,
        })),
        payment_mode: "COD",
      };

      const res = await api.post(
        "/orders",
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessage(res.data.message);

      setCart([]);
      setShowCheckout(false);

      // Refresh updated stock
      fetchProducts();

    } catch (err) {
      console.error(err);
      setMessage(
        err.response?.data?.detail ||
        "Order failed"
      );
    }
  };

  /*
    AUTH SCREEN
  */
  if (!token) {
    return (
      <div className="container">
        <h1>QuickCart Customer Portal</h1>

        {message && <div>{message}</div>}

        <div className="auth-box">
          <h2>
            {authMode === "login"
              ? "Login"
              : "Signup"}
          </h2>

          {authMode === "signup" && (
            <>
              <input
                placeholder="Name"
                onChange={(e) =>
                  setAuthForm({
                    ...authForm,
                    name: e.target.value,
                  })
                }
              />

              <input
                placeholder="Phone"
                onChange={(e) =>
                  setAuthForm({
                    ...authForm,
                    phone: e.target.value,
                  })
                }
              />

              <input
                placeholder="City"
                onChange={(e) =>
                  setAuthForm({
                    ...authForm,
                    city: e.target.value,
                  })
                }
              />

              <input
                placeholder="Area"
                onChange={(e) =>
                  setAuthForm({
                    ...authForm,
                    area: e.target.value,
                  })
                }
              />
            </>
          )}

          <input
            placeholder="Email"
            onChange={(e) =>
              setAuthForm({
                ...authForm,
                email: e.target.value,
              })
            }
          />

          <input
            type="password"
            placeholder="Password"
            onChange={(e) =>
              setAuthForm({
                ...authForm,
                password: e.target.value,
              })
            }
          />

          {authMode === "login" ? (
            <>
              <button onClick={handleLogin}>Login</button>

              <p onClick={() => setAuthMode("signup")}>
                Signup
              </p>
            </>
          ) : (
            <>
              <button onClick={handleSignup}>
                Signup
              </button>

              <p onClick={() => setAuthMode("login")}>
                Login
              </p>
            </>
          )}
        </div>
      </div>
    );
  }

  /*
    SHOPPING SCREEN
  */
  return (
    <div className="container">
      <div className="top-bar">
        <h1>QuickCart Store</h1>
        <button onClick={handleLogout}>
          Logout
        </button>
      </div>

      {message && <div>{message}</div>}

      <div className="layout">
        <div className="catalog">
          <h2>Products</h2>

          {products.map((product) => (
            <div key={product.product_id}>
              <h3>{product.product_name}</h3>
              <p>₹{product.price}</p>
              <p>Stock: {product.stock_qty}</p>

              <button
                disabled={product.stock_qty <= 0}
                onClick={() => addToCart(product)}
              >
                Add
              </button>
            </div>
          ))}
        </div>

        <div className="cart">
          <h2>Cart</h2>

          {cart.map((item) => (
            <div key={item.product_id}>
              <p>{item.product_name}</p>
              <p>Qty: {item.qty}</p>
              <p>₹{item.line_total}</p>

              <button
                onClick={() =>
                  increaseQty(item.product_id)
                }
              >
                +
              </button>

              <button
                onClick={() =>
                  decreaseQty(item.product_id)
                }
              >
                -
              </button>

              <button
                onClick={() =>
                  removeItem(item.product_id)
                }
              >
                Remove
              </button>
            </div>
          ))}

          <h3>Total: ₹{cartTotal}</h3>

          {!showCheckout && cart.length > 0 && (
            <button
              onClick={() =>
                setShowCheckout(true)
              }
            >
              Checkout
            </button>
          )}

          {showCheckout && (
            <button onClick={placeOrder}>
              Place Order
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;