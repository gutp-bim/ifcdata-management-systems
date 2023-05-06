import { useState } from 'react'
import * as Reactstrap from "reactstrap"
import { Link } from "react-router-dom"

import { ModalState } from './state'
import UploadModal from './UploadModal'
import DeleteModal from './DeleteModal'
import { routes } from "main/routes"
import { useGetModels } from 'apiServices/getModels'
import { MetaDataModel } from 'innerDataModel/MetaDataModel';

const View = () => {
  const [modalState, setModalState] = useState<ModalState>('None')
  const [targetIfcModelId, setTargetIfcModelId] = useState<string>('')
  const models: MetaDataModel[] = useGetModels()
  return (
    <div>
      <Reactstrap.Card className="card-item">
        <Reactstrap.CardHeader>
          <div className="d-flex flex-row justify-content-between">
            <span>モデル選択</span>
            <Reactstrap.Button color='success' active onClick={() => setModalState('Upload')}>
              モデル追加
            </Reactstrap.Button>
            <UploadModal modalState={modalState} setModalState={setModalState} />
            <DeleteModal ifcModelId={targetIfcModelId} modalState={modalState} setModalState={setModalState} />
          </div>
        </Reactstrap.CardHeader>
        <Reactstrap.CardBody>
          <Reactstrap.Table>
            <thead>
              <tr>
                <th>名前</th>
                <th>説明</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {models.map((model: MetaDataModel) => {
                return (
                  <tr key={model.id}>
                    <td>
                      <Link to={routes.models.item.view.buildURL({modelId: model.id})}>
                        {model.name}
                      </Link>
                    </td>
                    <td>{model.description}</td>
                    <td>
                      <Reactstrap.Button
                        color='danger'
                        active
                        onClick={() => {
                          setTargetIfcModelId(model.id)
                          setModalState('Delete')
                        }}>
                        削除
                      </Reactstrap.Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Reactstrap.Table>
        </Reactstrap.CardBody>
      </Reactstrap.Card>
    </div>
  );
}

export default View;