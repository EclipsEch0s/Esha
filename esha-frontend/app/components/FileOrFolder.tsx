import React from 'react'
import FileOrFolderCard from './FileOrFolderCard'

const FileOrFolder: React.FC = () => {
    return (
        <div className='flex space-x-5 mx-5 mt-2 flex-wrap'>
            <FileOrFolderCard isFolder={true} name="C" />
            <FileOrFolderCard isFolder={false} name="py"/>
            <FileOrFolderCard isFolder={true} name="rust"/>
        </div>
    )
}

export default FileOrFolder