import React from 'react'

interface ESHA_ChatProps {
    msg: String
}

const ESHA_Chat: React.FC<ESHA_ChatProps> = ({ msg }) => {
    return (
        <div className="chat chat-start">
            <div className="chat-header">
                E.S.H.A
                {/* <time className="text-xs opacity-50">12:45</time> */}
            </div>
            <div className="chat-bubble">{msg}</div>
        </div>

    )
}

export default ESHA_Chat