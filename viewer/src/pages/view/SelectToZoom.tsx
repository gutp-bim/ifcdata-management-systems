import { useContext, useEffect } from 'react';

import { guidContext } from './contexts';
import { useBounds } from './Bounds'

import { useThree } from '@react-three/fiber';

const SelectToZoom = () => {
    const scene = useThree((state) => state.scene)
    const boundsApi = useBounds()
    const ctx = useContext(guidContext)
    useEffect(() => {
        const object = scene.getObjectByName(ctx.guid)
        boundsApi.refresh(object).fit()
    }, [ctx.guid])
    
    return <></>
}

export default SelectToZoom
