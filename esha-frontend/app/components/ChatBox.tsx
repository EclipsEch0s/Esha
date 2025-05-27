import React from 'react';
import ESHA_Chat from './ESHA_Chat';
import UserChat from './UserChat';

interface ChatMessage {
  sender: "user" | "esha";
  text: string;
}

interface ChatBoxProps {
  messages: ChatMessage[];
}

const ChatBox: React.FC<ChatBoxProps> = ({ messages }) => {
  return (
    <>
      {messages.map((msg, index) =>
        msg.sender === "esha" ? (
          <ESHA_Chat key={index} msg={msg.text} />
        ) : (
          <UserChat key={index} msg={msg.text} />
        )
      )}
    </>
  );
};

export default ChatBox;
