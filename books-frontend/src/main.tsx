import * as React from 'react'
import * as ReactDOM from 'react-dom'
import { Provider, connect } from 'react-redux'
import DjangoCSRFToken from 'django-react-csrftoken'
import {createStore, Store, combineReducers} from 'redux'

import * as _ from 'lodash'


export interface Book_ {
    id: number
    title: string
    author: string

    wikipedia_url: string
    gutenberg_url: string
    adelaide_url: string

    isbn_10: string
    isbn_13: string

}


interface SearchProps {
    dispatch: Function
}

interface SearchState {
    value: string
}

class SearchForm extends React.Component<SearchProps, SearchState> {
    constructor(props: SearchProps) {
        super(props);
        this.state = {value: ''}

        this.handleChange = this.handleChange.bind(this)
    }

    handleChange(event) {
        this.setState({value: event.target.value})
    }

    render() {
        return (
            <form style={{}}>
                <label>
                    Search by title, author, or ISBN:
                    <input type="text" name="search"
                           onChange={this.handleChange}/>
                </label>
                {/*<input type="submit" value="Submit" />*/}
                <button type="button" value="Submit"
                        onClick={ () => search(this.state.value) }
                >Search</button>
            </form>
        )
    }
}

const Book = ({book}: {book: Book_}) => (
    <div>
    <h4>{book.title}, written by: {book.author}</h4>
        <div style={{float: 'left', width: 300, height: 100, background: 'teal'}}>
            <a href={book.wikipedia_url}>Wikipedia</a>
        </div>
        <div style={{float: 'left', width: 300, height: 100, background: 'salmon'}}>

        </div>

    </div>

)


// todo figure out what type the store is.
const Main = ({store}: {store: any}) => {
     return (
        <div>
            <h1>Find free digital books</h1>

            <SearchForm />

            { gstore.getState().books.map(b => <Book key={b.id} book={b}/>) }
        </div>
    )
}


function get(url: string, callback: any=() => null) {
    // Send a post request to the server; parse the response as JSON.
    let getCookie = null
    // fetch may fail on IE without a backwards-compatible version.
    fetch(url, {
        method: 'GET',
        headers: {
            // "X-CSRFToken": getCookie('csrftoken'),
            // "Content-Type": "application/json; charset=UTF-8",
            // "Accept": "application/json",
            // "X-Requested-With": "XMLHttpRequest"
            'Authorization': 'Basic '+btoa('admin:okokokok'),
        },
        // credentials: 'include',
        // body: JSON.stringify(data)
    })

    // Parse JSON if able.
        .then(result => {
            try {
                return result.json()
            } catch(e) {
                return result
            }
        })
        .then(callback)
}


function post(url: string, data, callback: any=() => null) {
    // Send a post request to the server; parse the response as JSON.
    let getCookie = null
    // fetch may fail on IE without a backwards-compatible version.
    fetch(url, {
        method: 'POST',
        headers: {
            // "X-CSRFToken": getCookie('csrftoken'),
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        },
        credentials: 'include',
        body: JSON.stringify(data)
    })

    // Parse JSON if able.
        .then(result => {
            try {
                return result.json()
            } catch(e) {
                return result
            }
        })
        .then(callback)
}


function search(query: string) {
    // Query the server with a search.
    const data = {
        // type: 'search'
        query: query,
    }

    const success = (response) => {
        console.log("success:", response)
    }
    post('http://127.0.0.1:8000/main/search', data, success)
}


// State and initialization below this line.

interface mainState {
    page: string
    books: Book_[]
}

const initialState: mainState = {
    page: 'front',
    books: [
        {
            title: "Snow Clash",
            author: "Asimov",
            id: -99,

            wikipedia_url: 'http://wiki.org',
            gutenberg_url: '',
            adelaide_url: 'http://australia',

            isbn_10: "asdf",
            isbn_13: "kkkk",
        }
    ],
}

const mainReducer = (state: mainState=initialState, action: any) => {
    // Misc config variables not related to the current schedule.
    // todo figure out how to add types to these
    switch (action.type) {
        case 'changePage':
            return {...state, page: action.page}

        case 'addBooks':
            return{...state, books: state.books.concat(action.books)}

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
const mapStateToProps = (state) => ({ store: state })
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


get('http://127.0.0.1:8000/main/books', (resp) => {
    gstore.dispatch({
        type: 'addBooks',
        books: resp
    })
})

ReactDOM.render(
    <Provider store={gstore}>
        <Connected />
    </Provider>, document.getElementById('react')
)
