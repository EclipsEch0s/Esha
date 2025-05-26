import React from 'react'

interface UserChatProps {
    userName?: String,
    msg: String
}

const UserChat: React.FC<UserChatProps> = ({ userName = "user", msg }) => {
    return (
        <div className="chat chat-end">
            <div className="chat-image avatar">
            </div>
            <div className="chat-header">
                {userName}
                <time className="text-xs opacity-50">12:46</time>
            </div>
            <div className="chat-bubble">{msg}</div>
        </div>
    )
}

export default UserChat