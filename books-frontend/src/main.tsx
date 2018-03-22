import * as React from 'react'
import * as ReactDOM from 'react-dom'
import { Provider, connect } from 'react-redux'
import DjangoCSRFToken from 'django-react-csrftoken'
import { createStore, Store, combineReducers } from 'redux'

import { Button, Grid, Row, Col, Clearfix,
    Form, FormGroup, FormControl, ControlLabel } from 'react-bootstrap';

import * as _ from 'lodash'


export interface Author {
    id: number
    first_name: string
    last_name: string
}

export interface Book_ {
    id: number
    title: string
    author: Author
    description: string

    wikipedia_url: string
    gutenberg_url: string
    adelaide_url: string
    amazon_url: string
    kobo_url: string
    google_url: string

    copyright_exp_us: string // date in format YYYY-MM-DD
    copyright_expired: boolean

    isbn_10: string
    isbn_13: string

}


interface SearchProps {
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
            <Form inline>
                <FormGroup controlId="searchBox" >
                    <ControlLabel>Search by title, author, or ISBN:</ControlLabel>
                    <FormControl
                        type="text"
                        value={this.state.value}
                        placeholder="Search by title or author"
                        onChange={this.handleChange}
                    />
                    <FormControl.Feedback />

                    <Button type="button"
                            onClick={ () => search(this.state.value) }
                    >Search</Button>
                </FormGroup>

            </Form>
        )
    }
}

const Book = ({book}: {book: Book_}) => (
    <div style={{marginTop: 40}}>
        <h4>{book.title}, written by: {book.author.last_name}</h4>

        <div style={{float: 'left', width: 300, height: 100, background: 'teal'}}>
            <h3>Information</h3>
            <a href={book.wikipedia_url}>Wikipedia</a>
            <a href={book.wikipedia_url}>Wikipedia</a>
        </div>

        <div style={{float: 'left', width: 300, height: 100, background: 'salmon'}}>
            <h3>Stores</h3>
            <a href={book.amazon_url}>Amazon</a>
            Kobo?
            Google

        </div>

    </div>

)


const HomePage = ({books}: {books: Book_[]}) => (
    <div>
        <h1>Find ebooks</h1>

        <SearchForm />

        { books.map(b => <Book key={b.id} book={b}/>) }
    </div>
)


const Menu = () => (
    <div>

    </div>
)



// todo figure out what type the store is.
const Main = ({store}: {store: any}) => {
    console.log(gstore.getState().books, "ALL")

    // todo treat gstore as if it were local here, then change to store once
    const page = gstore.getState().page  // code shortener
    let activePage = <HomePage books={gstore.getState().books}/>
    // if page == 'about' {
    // activePage = <AboutPage />
// }

    // we sort out how not to hvae it local.
    return (
        <div>
            <Grid>
                <Row className="show-grid">
                    <Col sm={12}>
                        <Menu />
                    </Col>
                </Row>

                <Row className="show-grid">
                    <Col sm={10} smOffset={1}>


                        { activePage }
                    </Col>
                </Row>
            </Grid>
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
    books: [],
}

const mainReducer = (state: mainState=initialState, action: any) => {
    // Misc config variables not related to the current schedule.
    // todo figure out how to add types to these
    switch (action.type) {
        case 'changePage':
            return {...state, page: action.page}

        case 'addBooks':
            return{...state, books: state.books.concat(action.books)}

        case 'replaceBooks':
            return{...state, books: action.books}

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
        type: 'replaceBooks',
        books: resp
    })
})

ReactDOM.render(
    <Provider store={gstore}>
        <Connected />
    </Provider>, document.getElementById('react')
)

// ReactDOM.render(<Main store={gstore} />, document.getElementById('react'))
