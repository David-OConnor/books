import * as React from 'react'
import * as ReactDOM from 'react-dom'
import { Provider, connect } from 'react-redux'
import DjangoCSRFToken from 'django-react-csrftoken'
import {createStore, Store, combineReducers} from 'redux'

import * as _ from 'lodash'


interface Book_ {
    id: number
    title: string
    author: string
    isbn_10: string
    isbn_13: string

}


const Book = ({book}: {book: Book_}) => (
    <h4>{book.title}, written by: {book.author}</h4>
)


// todo figure out what type the store is.
const Main = ({store}: {store: any}) => {
    console.log("TEST")
    return (
        <div>
            <h1>Hello World!</h1>

            { store.main.books.map(b => <Book book={b}/>) }
        </div>
    )
}



// State and initialization below this line.

interface mainState {
    page: string
    books: Book_[]
}

const initialState: mainState = {
    page: 'main',
    books: [
        {
            title: "Snow Clash",
            author: "Asimov",
            id: 0,
            isbn_10: "asdf",
            isbn_13: "kkkk",
        }
    ],
}

const mainReducer = (state: mainState=initialState, action: any) => {
    // Misc config variables not related to the current schedule.
    switch (action.type) {
        case 'changePage':
            return {...state, page: action.Page}

        default:
            return state
    }
}


let reducer = combineReducers({
    main: mainReducer,
})

const store: Store<any> = createStore(reducer)

// Connext the redux store to React.
const mapStateToProps = (state) => ({ store: state })
const Connected = connect(mapStateToProps)(Main)

ReactDOM.render(
    <Provider store={store}>
        <Connected />
    </Provider>, document.getElementById('react')
)
