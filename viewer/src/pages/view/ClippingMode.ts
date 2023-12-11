type Axis = 'x' | 'y' | 'z'
type Direction = 'positive' | 'negative'


export type ClippingMode = 
    {
        enableClip: false,
        toString: () => string
    } |
    {
        enableClip: true,
        axis: Axis,
        direction: Direction,
        toString: () => string
    }

export const ClippingMode = {
    noClip: (): ClippingMode => {
        return {
            enableClip: false,
            toString: () => 'no-clipping'
        }
    },
    clip: (axis: Axis, direction: Direction): ClippingMode => {
        return {
            enableClip: true,
            axis: axis,
            direction: direction,
            toString: () => `${axis}-${direction}`
        }
    },
    fromString: (mode: string): ClippingMode => {
        const axisDirectionRegex = /^(x|y|z)-(positive|negative)$/;
        if (axisDirectionRegex.test(mode)) {
            const axis = mode.split("-")[0] as Axis
            const direction = mode.split("-")[1] as Direction
            return {enableClip: true, axis: axis, direction: direction, toString: () => mode}
        } else return {enableClip: false, toString: () => 'no-clipping'}
    }
}

export const clippingModeOptions = [
    {value: ClippingMode.noClip().toString(), label: '断面切断なし'},
    {value: ClippingMode.clip('x', 'positive').toString(), label: 'x軸正方向切断'},
    {value: ClippingMode.clip('x', 'negative').toString(), label: 'x軸負方向切断'},
    {value: ClippingMode.clip('y', 'positive').toString(), label: 'y軸正方向切断'},
    {value: ClippingMode.clip('y', 'negative').toString(), label: 'y軸負方向切断'},
    {value: ClippingMode.clip('z', 'positive').toString(), label: 'z軸正方向切断'},
    {value: ClippingMode.clip('z', 'negative').toString(), label: 'z軸負方向切断'}
]
