import React, { useState } from 'react';
import * as Reactstrap from "reactstrap"

import { ModalState } from './state';
import { deleteToModelServer, deleteToGeometryServer } from 'apiServices/deleteIfcFile';

const onClickSubmit = async (modelId: string) => {
    if (modelId === '') {
        return
    }
    const resToModelServer = await deleteToModelServer(modelId)
    const resToGeometryServer = await deleteToGeometryServer(modelId)
}

const DeleteModal: React.FC<{
    ifcModelId: string,
    modalState: ModalState,
    setModalState: React.Dispatch<React.SetStateAction<ModalState>>
}> = (props) => {
    const [isUploading, setIsUploading] = useState<boolean>(false)
    return (
        <Reactstrap.Modal isOpen={props.modalState === 'Delete'}>
            <Reactstrap.ModalHeader> IFCファイル削除 </Reactstrap.ModalHeader>
            <Reactstrap.ModalBody>
                {props.ifcModelId} を削除します。<br/>
                この操作は取り消せません。よろしいですか？<br/>
                なお、この操作が反映されるには30分ほどかかります。
            </Reactstrap.ModalBody>
            <Reactstrap.ModalFooter>
                <Reactstrap.Button
                    color='danger'
                    active>
                    削除
                </Reactstrap.Button>
                <Reactstrap.Button
                    color='secondary'
                    active
                    onClick={() => {props.setModalState('None')}}>
                    キャンセル
                </Reactstrap.Button>
            </Reactstrap.ModalFooter>
        </Reactstrap.Modal>
    )
}

export default DeleteModal