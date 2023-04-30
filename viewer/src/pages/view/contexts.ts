import { createContext, useCallback, useState } from 'react' 

type GuidContext = {
    guid: string;
    setNewGuid: (guid: string) => void;
  }
  
const defaultContext: GuidContext = {
    guid: "",
    setNewGuid: () => {}
}
  
export const guidContext = createContext<GuidContext>(defaultContext);
  
export const useGuidContext = (): GuidContext => {
    const [guid, setGuid] = useState("");
    const setNewGuid = useCallback((newGuid: string): void => {
      setGuid(newGuid);
    }, []);
    return {
      guid,
      setNewGuid
    }
}