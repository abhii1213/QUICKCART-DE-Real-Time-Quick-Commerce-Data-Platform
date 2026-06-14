import { useEffect, useState } from "react";
import "./App.css";
import { api } from "./services/api";

function App() {
  const [token, setToken] = useState(localStorage.getItem("quickcart_token"));

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
  const [searchText, setSearchText] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [cart, setCart] = useState([]);
  const [showCheckout, setShowCheckout] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);

  /*
    Fetch product catalog
  */
  const fetchProducts = async () => {
    try {
      const res = await api.get("/products");
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  /*
    Load products after login
  */
  useEffect(() => {
    if (token) {
      fetchProducts();
    }
  }, [token]);

  /*
    Debounce search input
    Prevent Kafka event spam on every keystroke
  */
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchText);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchText]);

  /*
    Track only final debounced search
  */
  useEffect(() => {
    if (debouncedSearch.trim() && token) {
      trackActivity("PRODUCT_SEARCHED", {
        search_text: debouncedSearch,
      });
    }
  }, [debouncedSearch]);

  /*
    Generic customer activity tracker
  */
  const trackActivity = async (eventType, payload) => {
    try {
      await api.post(
        "/activity/track",
        {
          event_type: eventType,
          payload,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
    } catch (err) {
      console.error("Activity tracking failed:", err);
    }
  };

  /*
    Signup
  */
  const handleSignup = async () => {
    try {
      const res = await api.post("/auth/signup", authForm);

      localStorage.setItem("quickcart_token", res.data.access_token);

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

      localStorage.setItem("quickcart_token", res.data.access_token);

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
    setSearchText("");
    setDebouncedSearch("");
    setMessage("");
  };

  /*
    Search handler
    UI updates immediately
    Analytics handled by debounce
  */
  const handleSearch = (value) => {
    setSearchText(value);
  };

  /*
    Add item to cart
  */
  const addToCart = (product) => {
    const existing = cart.find(
      (item) => item.product_id === product.product_id,
    );

    if (existing) {
      if (existing.qty >= product.stock_qty) {
        setMessage("Stock limit reached.");
        trackActivity("OUT_OF_STOCK_INTEREST", {
          product_id: product.product_id,
        });
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
            : item,
        ),
      );

      trackActivity("CART_QTY_INCREASED", {
        product_id: product.product_id,
      });
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

      trackActivity("CART_ITEM_ADDED", {
        product_id: product.product_id,
        qty: 1,
      });
    }
  };

  /*
  Product viewed
*/
  const viewProduct = (product) => {
    setSelectedProduct(product);

    trackActivity("PRODUCT_VIEWED", {
      product_id: product.product_id,
    });
  };

  /*
    Increase cart quantity
  */
  const increaseQty = (product_id) => {
    setCart(
      cart.map((item) => {
        if (item.product_id === product_id) {
          if (item.qty >= item.available_stock) {
            setMessage("Stock limit reached.");
            return item;
          }

          return {
            ...item,
            qty: item.qty + 1,
            line_total: (item.qty + 1) * item.unit_price,
          };
        }

        return item;
      }),
    );

    trackActivity("CART_QTY_INCREASED", {
      product_id,
    });
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
        .filter(Boolean),
    );

    trackActivity("CART_QTY_DECREASED", {
      product_id,
    });
  };

  /*
    Remove cart item
  */
  const removeItem = (product_id) => {
    setCart(cart.filter((item) => item.product_id !== product_id));

    trackActivity("CART_ITEM_REMOVED", {
      product_id,
    });
  };

  /*
    Checkout started
  */
  const startCheckout = () => {
    setShowCheckout(true);

    trackActivity("CHECKOUT_STARTED", {
      cart_size: cart.length,
      cart_total: cartTotal,
    });
  };

  /*
    Cart total
  */
  const cartTotal = cart.reduce((sum, item) => sum + item.line_total, 0);

  /*
    Real order placement
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

      const res = await api.post("/orders", payload, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setMessage(res.data.message);

      setCart([]);
      setShowCheckout(false);

      fetchProducts();
    } catch (err) {
      console.error(err);

      setMessage(err.response?.data?.detail || "Order failed");
    }
  };

  /*
    Product filtering
  */
  const filteredProducts = products.filter((product) =>
    product.product_name.toLowerCase().includes(searchText.toLowerCase()),
  );

  /*
    ==================================================
    AUTH SCREEN UI
    ==================================================
  */
  if (!token) {
    return (
      <div className="auth-wrapper">
        {/* Global Toast Message */}
        {message && <div className="toast-message">{message}</div>}

        <div className="auth-box">
          <div className="auth-header">
            <h1>QuickCart</h1>
            <p>Your daily essentials, delivered fast.</p>
          </div>

          <h2>{authMode === "login" ? "Welcome Back" : "Create an Account"}</h2>

          <div className="auth-form">
            {authMode === "signup" && (
              <div className="form-grid">
                <input
                  type="text"
                  placeholder="Full Name"
                  onChange={(e) =>
                    setAuthForm({ ...authForm, name: e.target.value })
                  }
                />
                <input
                  type="tel"
                  placeholder="Phone Number"
                  onChange={(e) =>
                    setAuthForm({ ...authForm, phone: e.target.value })
                  }
                />
                <input
                  type="text"
                  placeholder="City"
                  onChange={(e) =>
                    setAuthForm({ ...authForm, city: e.target.value })
                  }
                />
                <input
                  type="text"
                  placeholder="Area"
                  onChange={(e) =>
                    setAuthForm({ ...authForm, area: e.target.value })
                  }
                />
              </div>
            )}

            <input
              type="email"
              placeholder="Email Address"
              onChange={(e) =>
                setAuthForm({ ...authForm, email: e.target.value })
              }
            />

            <input
              type="password"
              placeholder="Password"
              onChange={(e) =>
                setAuthForm({ ...authForm, password: e.target.value })
              }
            />

            <div className="auth-actions">
              {authMode === "login" ? (
                <>
                  <button
                    className="btn-primary btn-block"
                    onClick={handleLogin}
                  >
                    Login
                  </button>
                  <p className="auth-toggle">
                    Don't have an account?{" "}
                    <span onClick={() => setAuthMode("signup")}>Sign up</span>
                  </p>
                </>
              ) : (
                <>
                  <button
                    className="btn-primary btn-block"
                    onClick={handleSignup}
                  >
                    Signup
                  </button>
                  <p className="auth-toggle">
                    Already have an account?{" "}
                    <span onClick={() => setAuthMode("login")}>Log in</span>
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  /*
    ==================================================
    SHOPPING SCREEN UI
    ==================================================
  */
  return (
    <div className="app-container">
      {/* Global Toast Message */}
      {message && <div className="toast-message active">{message}</div>}

      {/* Top Navigation */}
      <header className="top-bar">
        <div className="top-bar-content">
          <h1>🛒 QuickCart</h1>

          <div className="search-container">
            <input
              type="text"
              className="search-input"
              placeholder="Search products..."
              value={searchText}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>

          <button className="btn-outline" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="shop-layout">
        {/* Product Catalog */}
        <section className="catalog-section">
          <div className="catalog-header">
            <h2>Products</h2>
            <span className="product-count">
              {filteredProducts.length} items found
            </span>
          </div>

          <div className="product-grid">
            {filteredProducts.length === 0 ? (
              <p className="empty-state">
                No products found matching your search.
              </p>
            ) : (
              filteredProducts.map((product) => (
                <div
                  className="product-card"
                  key={product.product_id}
                  onClick={() => viewProduct(product)}
                >
                  <div className="product-info">
                    <h3>{product.product_name}</h3>
                    <div className="product-meta">
                      <span className="price">₹{product.price}</span>
                      <span
                        className={`stock-badge ${product.stock_qty > 0 ? "in-stock" : "out-of-stock"}`}
                      >
                        {product.stock_qty > 0
                          ? `${product.stock_qty} left`
                          : "Out of stock"}
                      </span>
                    </div>
                  </div>
                  <button
                    className="btn-primary"
                    disabled={product.stock_qty <= 0}
                    onClick={(e) => {
                      e.stopPropagation();
                      addToCart(product);
                    }}
                  >
                    {product.stock_qty <= 0 ? "Unavailable" : "Add to Cart"}
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Shopping Cart Sidebar */}
        <aside className="cart-sidebar">
          <h2>Your Cart</h2>

          {cart.length === 0 ? (
            <div className="empty-cart">
              <p>Your cart is empty.</p>
              <span>Add items to get started!</span>
            </div>
          ) : (
            <div className="cart-items">
              {cart.map((item) => (
                <div className="cart-item" key={item.product_id}>
                  <div className="item-details">
                    <p className="item-name">{item.product_name}</p>
                    <p className="item-price">₹{item.line_total}</p>
                  </div>

                  <div className="item-controls">
                    <div className="qty-group">
                      <button onClick={() => decreaseQty(item.product_id)}>
                        -
                      </button>
                      <span>{item.qty}</span>
                      <button onClick={() => increaseQty(item.product_id)}>
                        +
                      </button>
                    </div>
                    <button
                      className="btn-remove"
                      onClick={() => removeItem(item.product_id)}
                      title="Remove item"
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Checkout Area */}
          <div className="cart-footer">
            <div className="cart-total">
              <span>Total:</span>
              <span>₹{cartTotal}</span>
            </div>

            {!showCheckout && cart.length > 0 && (
              <button className="btn-primary btn-block" onClick={startCheckout}>
                Proceed to Checkout
              </button>
            )}

            {showCheckout && (
              <div className="checkout-confirm">
                <p>
                  Payment Mode: <strong>Cash on Delivery</strong>
                </p>
                <button className="btn-success btn-block" onClick={placeOrder}>
                  Confirm & Place Order
                </button>
                <button
                  className="btn-text btn-block"
                  onClick={() => setShowCheckout(false)}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </aside>
      </main>
      <div>
        {selectedProduct && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>{selectedProduct.product_name}</h2>

              {/* <p>Product ID: {selectedProduct.product_id}</p> */}

              <p>Category: {selectedProduct.category}</p>

              <p>Price: ₹{selectedProduct.price}</p>

              <p>Available Stock: {selectedProduct.stock_qty}</p>

              <div className="modal-actions">
                <button
                  disabled={selectedProduct.stock_qty <= 0}
                  onClick={() => addToCart(selectedProduct)}
                >
                  {selectedProduct.stock_qty <= 0
                    ? "Out Of Stock"
                    : "Add To Cart"}
                </button>

                <button onClick={() => setSelectedProduct(null)}>Close</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
