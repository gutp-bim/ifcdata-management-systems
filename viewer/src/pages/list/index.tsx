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
  const [targetIfc, setTargetIfc] = useState<[string, string]>(['', ''])
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
            <DeleteModal ifcModelId={targetIfc[0]} ifcModelName={targetIfc[1]} modalState={modalState} setModalState={setModalState} />
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
                          setTargetIfc([model.id, model.name])
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