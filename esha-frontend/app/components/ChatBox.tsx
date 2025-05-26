"use client"
import React from 'react'
import FileOrFolder from './FileOrFolder'
import ESHA_Chat from './ESHA_Chat'
import UserChat from './UserChat'

const ChatBox: React.FC = () => {
    return (
        <>
            <ESHA_Chat msg={"How Can I help You"}/>
            <UserChat msg={"Hey Show me the projects"}/>

            <ESHA_Chat msg={"Here it is"}/>
            <FileOrFolder />
        </>
    )
}

export default ChatBox