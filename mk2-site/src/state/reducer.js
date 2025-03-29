export const initialState = {
  currentThreadId: null,
  followUpMode: false,
  discoverFilters: {
    topic: '',
    source: ''
  },
};

function reducer(state, action) {
  switch(action.type) {
    case 'SET_THREAD':
      return { ...state, currentThreadId: action.payload };
    case 'TOGGLE_FOLLOW_UP':
      return { ...state, followUpMode: !state.followUpMode };
    case 'SET_DISCOVER_FILTERS':
      return { ...state, discoverFilters: action.payload };
    default:
      return state;
  }
}

export default reducer;
