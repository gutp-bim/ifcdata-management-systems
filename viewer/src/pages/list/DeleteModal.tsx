import React, { useState } from 'react';
import * as Reactstrap from "reactstrap"

import { ModalState } from './state';
import { deleteToModelServer, deleteToGeometryServer } from 'apiServices/deleteIfcFile';

const onClickSubmit = async (modelId: string) => {
    console.log("click")
    if (modelId === '') {
        return
    }
    const resToModelServer = await deleteToModelServer(modelId)
    console.log(resToModelServer)
    const resToGeometryServer = await deleteToGeometryServer(modelId)
    console.log(resToGeometryServer)
}

const DeleteModal: React.FC<{
    ifcModelId: string,
    ifcModelName: string,
    modalState: ModalState,
    setModalState: React.Dispatch<React.SetStateAction<ModalState>>
}> = (props) => {
    return (
        <Reactstrap.Modal isOpen={props.modalState === 'Delete'}>
            <Reactstrap.ModalHeader> IFCファイル削除 </Reactstrap.ModalHeader>
            <Reactstrap.ModalBody>
                {props.ifcModelName} を削除します。<br/>
                この操作は取り消せません。よろしいですか？<br/>
                なお、この操作が反映されるには30分ほどかかります。
            </Reactstrap.ModalBody>
            <Reactstrap.ModalFooter>
                <Reactstrap.Button
                    color='danger'
                    active
                    onClick={() => {onClickSubmit(props.ifcModelId)}}
                >
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