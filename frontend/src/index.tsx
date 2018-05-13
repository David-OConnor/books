import * as React from 'react';
import * as ReactDOM from 'react-dom'
import registerServiceWorker from './registerServiceWorker'

// redux-first-router imports
import {connectRoutes, NOT_FOUND} from 'redux-first-router'
import {combineReducers, createStore, applyMiddleware, compose} from 'redux'
import {Provider, connect, Dispatch} from 'react-redux'
import createHistory from 'history/createBrowserHistory'

import axios from "axios"

import {Main, BASE_URL} from './main'
import {MainState} from "./interfaces"

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
    displayLanguage: 'any'  // could be 'en', 'es', 'it', 'any'.
}

const mainReducer = (state: MainState=initialState, action: any) => {
    // Misc config variables not related to the current schedule.
    // todo figure out how to add types to these
    switch (action.type) {
        // case 'changePage':
        //     return {...state, page: action.page}

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

        case 'setDisplayLanguage':
            return {...state, displayLanguage: action.language}

        // Routing here
        case 'HOME':
            return {...state, page: 'home'}

        case 'RESOURCES':
            return {...state, page: 'resources'}
        case 'ABOUT':
            return {...state, page: 'about'}
        case NOT_FOUND:
            return null

        default:
            return state
    }
}

// Routing code here:
// https://github.com/faceyspacey/redux-first-router
const history = createHistory()

const routesMap = {
  HOME: '/',      // action <-> url path
  RESOURCES: '/resources',
  ABOUT: '/about'
}

const {reducer, middleware, enhancer} = connectRoutes(history, routesMap) // yes, 3 redux aspects

const rootReducer = combineReducers({location: reducer, main: mainReducer})
const middlewares = applyMiddleware(middleware)
// note the order: enhancer, then middlewares
const store = createStore(rootReducer, compose(enhancer, middlewares))

// Connext the redux store to React.
const mapStateToProps = (state: MainState) => ({ state: state })
const mapDispatchToProps = (dispatch: Dispatch<any>) => ({ dispatch: dispatch })

const Connected = connect(mapStateToProps, mapDispatchToProps)(Main)

// Populate resources.
axios.get(BASE_URL + 'resources').then(
    (resp) =>
        store.dispatch({
            type: 'replaceResources',
            resources: resp.data.results
        })
)

ReactDOM.render(
    <Provider store={store}>
        <Connected />
    </Provider>,
    document.getElementById('root') as HTMLElement
)
registerServiceWorker()
