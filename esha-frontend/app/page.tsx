'use client';

import React, { useState } from 'react';
import ChatBox from './components/ChatBox';
import { RiSendPlaneFill } from "react-icons/ri";
import Image from 'next/image';
import Rings from './components/Rings';

interface ChatMessage {
  sender: "user" | "esha";
  text: string;
}

const Home: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    { sender: "esha", text: "How Can I help You" },
  ]);

  const callEsha = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    // Add user's message immediately
    setMessages(prev => [...prev, { sender: "user", text: prompt }]);

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        cache: "no-store",
        body: JSON.stringify({ prompt })
      });

      const data = await response.json();

      // Add Esha's response to chat
      setMessages(prev => [...prev, { sender: "esha", text: data.response }]);
    } catch (err) {
      console.error("Error talking to Esha:", err);
      setMessages(prev => [...prev, { sender: "esha", text: "Sorry, something went wrong." }]);
    }

    setPrompt('');
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-base-200">
      <div className="w-1/2 p-4 h-[90vh] flex flex-col border rounded-lg shadow">
        {/* Scrollable chat area */}
        <div className="flex-1 overflow-y-auto mb-4 pr-2">
          <ChatBox messages={messages} />
        </div>

        {/* Input box pinned to bottom */}
        <form onSubmit={callEsha} className="relative">
          <input
            type="text"
            placeholder="Type here..."
            className="input input-bordered w-full focus:outline-none pr-10"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <button type="submit" aria-label="Send message">
            <RiSendPlaneFill className="absolute right-2 top-1/2 -translate-y-1/2 text-lg text-primary z-10" />
          </button>
        </form>
      </div>
      {/* <Image
        src="/ESHA_LOGO.png"   // Path relative to the public/ folder
        alt="My photo"
        width={300}                 // Required width in pixels
        height={200}                // Required height in pixels
        className='breathing absolute bottom-0 left-0' */}
      {/* /> */}
      <Rings />
    </div>
  );
};

export default Home;
