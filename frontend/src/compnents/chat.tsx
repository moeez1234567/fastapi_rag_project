import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Paperclip,
  Menu,
  X,
  FileText,
  MessageSquare,
} from "lucide-react";
import { useNavigate } from "react-router-dom"; // <-- Make sure this is imported
import "./chat.css";

// Interface definitions remain the same
interface Message {
  sender: "user" | "bot";
  text: string;
}

interface QAItem {
  question: string;
  answer: string;
}

interface UserHistory {
  q_a: QAItem[];
  user_name: string;
  points: string[];
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      text: "Hello! I'm your AI assistant. Select uploaded file for better response feel free to ask me anything!",
    },
  ]);
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userHistory, setUserHistory] = useState<UserHistory | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate(); // <-- This is the key line to get the navigation function

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch user history on component mount
  useEffect(() => {
    fetchUserHistory();
  }, []);

  const fetchUserHistory = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8001/user_history", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setUserHistory(data);
      }
    } catch (error) {
      console.error("Error fetching user history:", error);
    }
  };

  const sendMessage = async () => {
    if (!question.trim()) return;

    const userMessage: Message = {
      sender: "user",
      text: file.trim()
        ? `Question: ${question} | File: ${file}`
        : `Question: ${question}`,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await fetch("http://127.0.0.1:8001/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(
          file.trim()
            ? { question: question, file: file }
            : { question: question }
        ),
        credentials: "include",
      });

      const data = await response.json();
      console.log("Backend response:", data);

      const botMessage: Message = {
        sender: "bot",
        text: data.answer || "No response",
      };

      setMessages((prev) => [...prev, botMessage]);

      // Refresh user history after sending a message
      fetchUserHistory();
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        sender: "bot",
        text: "⚠️ Error connecting to server.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }

    setQuestion("");
    setFile("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const loadPreviousChat = (qaItem: QAItem) => {
    setMessages([
      {
        sender: "bot",
        text: "Hello! I'm your AI assistant. Feel free to ask me anything!",
      },
      {
        sender: "user",
        text: qaItem.question,
      },
      {
        sender: "bot",
        text: qaItem.answer,
      },
    ]);
  };

  const selectFile = (fileName: string) => {
    setFile(fileName);
  };

  return (
    <div className="chat-app">
      {/* Sidebar (unchanged) */}
      <div className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <div className="user-info">
            <div className="user-avatar">
              <User size={20} />
            </div>
            <div className="user-details">
              <h3>{userHistory?.user_name || "User"}</h3>
              <span className="user-status">Online</span>
            </div>
          </div>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <div className="sidebar-content">
          <div className="sidebar-section">
            <div className="section-header">
              <MessageSquare size={16} />
              <h4>Previous Chats</h4>
            </div>
            <div className="chat-history">
              {userHistory?.q_a.map((qaItem, index) => (
                <div
                  key={index}
                  className="history-item"
                  onClick={() => loadPreviousChat(qaItem)}
                >
                  <div className="history-question">
                    {qaItem.question.length > 50
                      ? `${qaItem.question.substring(0, 50)}...`
                      : qaItem.question}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-section">
            <div className="section-header">
              <FileText size={16} />
              <h4>Uploaded Files</h4>
            </div>
            <div className="files-list">
              {userHistory?.points.map((fileName, index) => (
                <div
                  key={index}
                  className="file-item"
                  onClick={() => selectFile(fileName)}
                >
                  <Paperclip size={14} />
                  <span className="file-name">{fileName}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Container (unchanged) */}
      <div
        className={`chat-container ${
          sidebarOpen ? "with-sidebar" : "full-width"
        }`}
      >
        <div className="chat-header">
          <div className="header-content">
            {!sidebarOpen && (
              <button
                className="sidebar-toggle-main"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu size={20} />
              </button>
            )}
            <div className="bot-avatar">
              <Bot size={24} />
            </div>
            <div className="header-text">
              {/* Moved upload button with text */}
              <button
                onClick={() => navigate("/upload")} // <-- 'navigate' is now correctly defined here
                className="upload-button"
              >
                <Paperclip size={20} />
                <span className="upload-text">Upload your files</span>
              </button>
            </div>
          </div>
        </div>

        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.sender}`}>
              <div className="message-avatar">
                {msg.sender === "user" ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div className="message-content">
                <div className="message-bubble">{msg.text}</div>
                <div className="message-time">
                  {new Date().toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="message-wrapper bot">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="message-bubble typing">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Updated Input Box */}
        <div className="input-box">
          <div className="input-container">
            {file && (
              <div className="file-preview">
                <Paperclip size={16} />
                <span>{file}</span>
                <button onClick={() => setFile("")} className="remove-file">
                  ×
                </button>
              </div>
            )}

            <div className="input-row">
              <div className="question-input-container">
                <textarea
                  value={question}
                  placeholder="Type your message here..."
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="question-input"
                  rows={1} // Keep rows at 1 for a shorter input box initially
                />

                <button
                  onClick={sendMessage}
                  className="send-button"
                  disabled={!question.trim()}
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
