import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";  // 👈 add this
import "./login.css";

interface AuthProps {
  onAuthSuccess: () => void;
}

const Sign_in: React.FC<AuthProps> = ({ onAuthSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  const navigate = useNavigate(); // 👈 create navigate hook

  // Auto slide to sign in after successful sign up
  useEffect(() => {
    if (message.includes("successfuly Sign-Up")) {
      setTimeout(() => {
        setIsSignUp(false);
        setMessage("Now please sign in with your credentials");
        setMessageType("success");
      }, 2000);
    }
  }, [message]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username || !formData.email || !formData.password) {
      setMessage("Please fill in all fields");
      setMessageType("error");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8001/submit_pass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();
      setMessage(data.message);

      if (data.message.includes("already Exist")) {
        setMessageType("error");
      } else {
        setMessageType("success");
        setFormData({ username: "", email: "", password: "" });
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("⚠️ Error connecting to server");
      setMessageType("error");
    }
    setIsLoading(false);
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username || !formData.password) {
      setMessage("Please enter username and password");
      setMessageType("error");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8001/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
        }),
        credentials: "include",
      });

      const data = await response.json();
      setMessage(data.message);

      if (data.message === "Login Successful !") {
        setMessageType("success");
        setTimeout(() => {
          onAuthSuccess();
          navigate("/chat"); // 👈 go to Chat.tsx
        }, 1500);
      } else {
        setMessageType("error");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("⚠️ Error connecting to server");
      setMessageType("error");
    }
    setIsLoading(false);
  };

  const switchMode = () => {
    setIsSignUp(!isSignUp);
    setMessage("");
    setFormData({ username: "", email: "", password: "" });
  };
  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
        </div>
      </div>

      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">🤖</div>
          <h1 className="auth-title">
            {isSignUp ? "Create Account" : "Welcome Back"}
          </h1>
          <p className="auth-subtitle">
            {isSignUp
              ? "Join our AI chat community"
              : "Sign in to continue chatting"}
          </p>
        </div>

        {message && (
          <div className={`message ${messageType}`}>
            <div className="message-content">
              <span className="message-icon">
                {messageType === "success" ? "✅" : "❌"}
              </span>
              {message}
            </div>
          </div>
        )}

        <form
          onSubmit={isSignUp ? handleSignUp : handleSignIn}
          className="auth-form"
        >
          <div className="input-group">
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Username"
              className="auth-input"
              required
            />
            <span className="input-icon">👤</span>
          </div>

          {isSignUp && (
            <div className="input-group">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Email Address"
                className="auth-input"
                required
              />
              <span className="input-icon">✉️</span>
            </div>
          )}

          <div className="input-group">
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Password"
              className="auth-input"
              required
            />
            <span className="input-icon">🔒</span>
          </div>

          <button type="submit" className="auth-button" disabled={isLoading}>
            {isLoading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                Processing...
              </div>
            ) : (
              <>
                <span>{isSignUp ? "Create Account" : "Sign In"}</span>
                <span className="button-icon">➤</span>
              </>
            )}
          </button>
        </form>

        <div className="auth-switch">
          <p>
            {isSignUp ? "Already have an account?" : "Don't have an account?"}
            <button onClick={switchMode} className="switch-button">
              {isSignUp ? "Sign In" : "Sign Up"}
            </button>
          </p>
        </div>

        <div className="auth-footer">
          <div className="feature-list">
            <div className="feature-item">
              <span className="feature-icon">💬</span>
              <span>AI-Powered Chat</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📁</span>
              <span>File Support</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔒</span>
              <span>Secure & Private</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sign_in;
