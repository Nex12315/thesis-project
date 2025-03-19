// src/App.tsx
import React from "react";
import Header from "./components/Header";
import Chat from "./components/Chat";
import "./styles/App.css";

const App: React.FC = () => {
  return (
    <div className="app">
      <Header />
      <main className="app-main">
        <Chat />
      </main>
      <footer className="app-footer">
        <p>© 2024 Arctic Valley AI Advisor | Student Thesis Project</p>
      </footer>
    </div>
  );
};

export default App;
