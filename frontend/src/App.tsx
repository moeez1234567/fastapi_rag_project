import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./compnents/login";
import Chat from "./compnents/chat";
import Upload from "./compnents/upload";


function App() {
  const handleAuthSuccess = () => {
    console.log("User logged in!");
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login onAuthSuccess={handleAuthSuccess} />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
