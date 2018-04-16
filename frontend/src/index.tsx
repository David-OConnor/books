import * as React from 'react';
import * as ReactDOM from 'react-dom'
import registerServiceWorker from './registerServiceWorker'

import {createStore, Store} from 'redux'
import {Provider, connect, Dispatch} from 'react-redux'

import axios from "axios"

import {Main, BASE_URL} from './main'
// import * as main from './main'
import {MainState} from "./interfaces";

// This module contains state and initialization code.

const initialState: MainState = {
    page: 'home',
    books: [],
    resources: [],
    loading: false,
    displayingResults: false,
    reportSubmitted: false,
    // SearchedTitle and Author are for passing reports; the main search field
    // data is stored in the SearchForm state.
    searchedTitle: '',
    searchedAuthor: '',
}

const mainReducer = (state: MainState=initialState, action: any) => {
    // Misc config variables not related to the current schedule.
    // todo figure out how to add types to these
    switch (action.type) {
        case 'changePage':
            return {...state, page: action.page}

        case 'addBooks':
            return {...state, books: state.books.concat(action.books)}

        case 'replaceBooks':
            return {...state, books: action.books}

        case 'replaceResources':
            return {...state, resources: action.resources}

        // todo combine boolean reducers?
        case 'setLoading':
            return {...state, loading: action.on}

        case 'setDisplaying':
            return {...state, displayingResults: action.on}

        case 'setReportSubmitted':
            return {...state, reportSubmitted: action.on}

        case 'setBool':
            return {...state, [action.item]: action.on}

        case 'setSearched':
            return {...state, searchedTitle: action.title, searchedAuthor: action.author}

        default:
            return state
    }
}

let store: Store<any> = createStore(mainReducer)

// Populate resources.
axios.get(BASE_URL + 'resources').then(
    (resp) =>
        store.dispatch({
            type: 'replaceResources',
            resources: resp.data.results
        })
)

// Connext the redux store to React.
const mapStateToProps = (state: MainState) => ({ state: state })
const mapDispatchToProps = (dispatch: Dispatch<any>) => ({ dispatch: dispatch })

const Connected = connect(mapStateToProps, mapDispatchToProps)(Main)

ReactDOM.render(
    <Provider store={store}>
        <Connected />
    </Provider>,
    document.getElementById('root') as HTMLElement
)
registerServiceWorker()
