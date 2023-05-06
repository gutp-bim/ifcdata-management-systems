import React, { useState } from 'react';
import * as Reactstrap from "reactstrap"
import Spinner from 'react-bootstrap/Spinner';

import { ModalState } from './state';
import { postToModelServer, postToGeometryServer } from 'apiServices/postIfcFile';

const onClickSubmit = async (file: File | undefined, name: string, description: string, setIsUploading: React.Dispatch<React.SetStateAction<boolean>>) => {
    setIsUploading(true)
    if (typeof file === 'undefined') {
        setIsUploading(false)
        return
    }
    const resToModelServer = await postToModelServer(file, name, description)
    if ('ifcmodel_id' in resToModelServer) {
        console.log('upload success')
        const newId = resToModelServer['ifcmodel_id']
        const resToGeometryServer = await postToGeometryServer(file, newId)
        console.log(resToGeometryServer)
        setIsUploading(false)
    } else {
        console.log('failed to upload')
        setIsUploading(false)
    }  
}

const UploadModal: React.FC<{
    modalState: ModalState,
    setModalState: React.Dispatch<React.SetStateAction<ModalState>>
}> = (props) => {
    const [file, setFile] = useState<File>()
    const [name, setName] = useState<string>("")
    const [description, setDescription] = useState<string>("")
    const [isUploading, setIsUploading] = useState<boolean>(false)
    return (
        <Reactstrap.Modal isOpen={props.modalState === 'Upload'}>
            <Reactstrap.ModalHeader> IFCファイル追加 </Reactstrap.ModalHeader>
            <Reactstrap.ModalBody>
                <label>ifc file :   </label>
                <input
                    type='file'
                    id='file'
                    name='file'
                    accept='.ifc,.step'
                    onChange={
                        (e) => {
                            if (e.target.files) {
                                setFile(e.target.files[0])
                            }
                        }
                    }
                 />
                 <br />
                <label>model name :  </label>
                <input
                    type='text'
                    id='name'
                    name='name'
                    placeholder='IFCモデル名'
                    onChange={(e) => setName(e.target.value)}
                    required
                />
                <br />
                <label>description :  </label>
                <input
                    type='text'
                    id='description'
                    name='description'
                    size={40}
                    placeholder='アップロードするIFCモデルに関する記述'
                    onChange={(e) => setDescription(e.target.value)}
                    required
                />
            </Reactstrap.ModalBody>
            <Reactstrap.ModalFooter>
                {
                    isUploading
                    ? <Reactstrap.Button
                            color='success'
                            active
                            disabled
                        >
                            <Spinner animation="border" size='sm'/>
                        </Reactstrap.Button>
                    : <Reactstrap.Button
                            color='success'
                            active
                            onClick={() => {
                                onClickSubmit(file, name, description, setIsUploading)
                            }}>
                            追加
                        </Reactstrap.Button>
                }
                <Reactstrap.Button color='secondary' active onClick={() => {
                    setName("")
                    setDescription("")
                    props.setModalState('None')
                }}>
                    キャンセル
                </Reactstrap.Button>
            </Reactstrap.ModalFooter>
        </Reactstrap.Modal>
    )
}

export default UploadModal