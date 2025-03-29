import React, { createContext, useReducer } from 'react';
import reducer, { initialState } from './reducer';

export const GlobalStateContext = createContext();

export function GlobalStateProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  return (
    <GlobalStateContext.Provider value={{ state, dispatch }}>
      {children}
    </GlobalStateContext.Provider>
  );
}
