import { useState } from 'react'
import * as Reactstrap from "reactstrap"
import { Link } from "react-router-dom"

import UploadModal from './UploadModal'
import { routes } from "main/routes"
import { useGetModels } from 'apiServices/getModels'
import { MetaDataModel } from 'innerDataModel/MetaDataModel';

const View = () => {
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false)
  const models: MetaDataModel[] = useGetModels()
  return (
    <div>
      <Reactstrap.Card className="card-item">
        <Reactstrap.CardHeader>
          <div className="d-flex flex-row justify-content-between">
            <span>モデル選択</span>
            <Reactstrap.Button color='success' active onClick={() => setIsModalOpen(true)}>
              モデル追加
            </Reactstrap.Button>
            <UploadModal isOpen={isModalOpen} setIsOpen={setIsModalOpen} />
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