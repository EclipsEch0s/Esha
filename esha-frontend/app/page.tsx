import React from 'react';
import ChatBox from './components/ChatBox';
import { RiSendPlaneFill } from "react-icons/ri";


const Home:React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-base-200">
      <div className="w-1/2 p-4 h-[90vh] flex flex-col border rounded-lg shadow">
        {/* Scrollable chat area */}
        <div className="flex-1 overflow-y-auto mb-4 pr-2">
          <ChatBox />
        </div>

        {/* Input box pinned to bottom */}
        <div className='relative'>
          <input
            type="text"
            placeholder="Type Or Say 'hey E.S.H.A'"
            className="input input-bordered w-full focus:outline-none pr-10"
          />
          <RiSendPlaneFill className="absolute right-2 top-1/2 -translate-y-1/2 text-lg text-primary z-10"/>
        </div>
      </div>
    </div>
  );
};

export default Home;
