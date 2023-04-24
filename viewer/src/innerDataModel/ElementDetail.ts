type Status = 'success' | 'failure' | 'loading'

export type ElementDetailResponse = 
    {status: 'success', info: Map<string, string>}
    | { status: 'failure' }
    | { status: 'loading' };

export const ElementDetailResponse = {
    success: (info: Map<string, string>): ElementDetailResponse => {
        return {status: 'success', info: info}
    },
    failure: (): ElementDetailResponse => {
        return {status: 'failure'}
    },
    loading: (): ElementDetailResponse => {
        return {status: 'loading'}
    }
}