import React from 'react'
import { FaFolder } from 'react-icons/fa'
import { FaFileAlt } from "react-icons/fa";

interface FileOrFolderProp {
    isFolder: Boolean,
    name: String
}

const FileOrFolderCard: React.FC<FileOrFolderProp> = ({ isFolder, name }) => {
    return (
        <div>
            {
                isFolder?
                    <FaFolder className = 'text-blue-600 text-4xl'/>:
                    <FaFileAlt className = 'text-blue-600 text-4xl' />
            }
            <span className='text-sm'>{name}</span>
        </div>
    )
}

export default FileOrFolderCard