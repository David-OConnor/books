import * as React from 'react'
import * as ReactDOM from 'react-dom'
import { Provider, connect } from 'react-redux'
import DjangoCSRFToken from 'django-react-csrftoken'
import {createStore, Store, combineReducers} from 'redux'

import * as _ from 'lodash'


interface Book {
    id: number
    title: string
    author: string
    isbn_10: string
    isbn_13: string

}


const Book = ({book}: {book: Book}) => (
    <h1>{book.title}, written by: {book.author}</h1>
)

// todo find out what type to use for store, reducers etc.
const Main = ({store}: {store: any}) => {

    return (
        <div>
            <h1>Hello World</h1>

            { store.main.books.map(b => <Book book={b}/>) }
        </div>
    )
}



// State and initialization below this line.

const initialState = {
    page: 'main',
    books: [],
}

const mainReducer = (state=initialState, action: any) => {
    // Misc config variables not related to the current schedule.
    switch (action.type) {
        case 'changePage':
            return {...state, page: action.Page}

    }
}


let reducer = combineReducers({
    main: mainReducer,
})

export let store: Store<any> = createStore(reducer)


// Connext the redux store to React.
const mapStateToProps = (state) => ({ main: state })
const ConnectedSchedules = connect(mapStateToProps)(Main)

export function render() {
    ReactDOM.render(
        <Provider store={store}>
            <ConnectedSchedules />
        </Provider>, document.getElementById('react')
    )
}