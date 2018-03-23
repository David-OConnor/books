import * as React from 'react';
import * as ReactDOM from 'react-dom'
import registerServiceWorker from './registerServiceWorker'

import { createStore, Store, combineReducers } from 'redux'
import { Provider, connect } from 'react-redux'

import Main from './main'
import * as main from './main'

// This module contains state and initialization code.

interface MainState {
    page: string
    books: main.Book2[]
    resources: main.Resource[]
}

const initialState: MainState = {
    page: 'home',
    books: [],

    // todo temp; store this in the database.
    resources: [
        {
            name: "Calibre",
            description: "Popular book viewer and editor with lots of options.",
            website_url: "https://calibre-ebook.com/",
            download_url: "https://calibre-ebook.com/download"
        },
        {
            name: "Microsoft Edge",
            description: "Epub viewer built into Windows 10",
            website_url: "https://calibre-ebook.com/",
            download_url: "https://calibre-ebook.com/download"
        },
        {
            name: "Moon+",
            description: "Popular book viewer for iOs and Android",
            website_url: "https://calibre-ebook.com/",
            download_url: "https://calibre-ebook.com/download"
        },
        {
            name: "Aldiko",
            description: "Popular book viewer for Android.",
            website_url: "http://www.aldiko.com/",
            download_url: "http://aldiko.com/download.html"
        },
    ],
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

        default:
            return state
    }
}

// let reducer = combineReducers({
//     main: mainReducer,
// })

// const store: Store<any> = createStore(reducer)

let gstore: Store<any> = createStore(mainReducer)

// Connext the redux store to React.
const mapStateToProps = (state) => ({ store: state, state: gstore.getState(),
    dispatch: gstore.dispatch })
// const mapDispatchToProps = (dispatch) => ({ dispatch: dispatch })
// todo sort this out later. Glob state for now
// const Connected = connect(
//     mapStateToProps,
//     // mapDispatchToProps
// )(Main)

const Connected = connect(
    mapStateToProps,
    // mapDispatchToProps
)(Main)

// main.get('http://127.0.0.1:8000/main/books', (resp) => {
//   gstore.dispatch({
//       type: 'replaceBooks',
//       books: resp
//   })
// })

ReactDOM.render(
    <Provider store={gstore}>
        <Connected />
    </Provider>,
    document.getElementById('root') as HTMLElement
)
registerServiceWorker()
