import * as React from 'react'

import DjangoCSRFToken from 'django-react-csrftoken'

import { Button, Grid, Row, Col, Clearfix,
    Form, FormGroup, FormControl, ControlLabel } from 'react-bootstrap';

import * as _ from 'lodash'

export interface Author {
    id: number
    first_name: string
    last_name: string
}

export interface Book2 {
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

export interface Resource {
    name: string
    description: string
    website_url: string
    download_url: string
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
            <Form inline={true}>
                <FormGroup controlId="searchBox" >
                    <ControlLabel>Search by title, author, or ISBN:</ControlLabel>
                    <FormControl
                        type="text"
                        value={this.state.value}
                        placeholder="Search by title or author"
                        onChange={this.handleChange}
                    />
                    <FormControl.Feedback />

                    <Button
                        type="button"
                        onClick={() => search(this.state.value)}
                    >Search
                    </Button>
                </FormGroup>

            </Form>
        )
    }
}

const Book = ({book}: {book: Book2}) => (
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

const HomePage = ({books}: {books: Book2[]}) => (
    <div>
        <h1>Find ebooks</h1>

        <SearchForm />

        {books.map(b => <Book key={b.id} book={b}/>)}
    </div>
)

const Resource = ({resource}: {resource: Resource}) => (
    <div>
        <h3>{resource.name}</h3>
        <p>{resource.description}</p>
        <a href={resource.website_url}>Website</a>
        <a href={resource.download_url}>Download</a>
    </div>
)

const ResourcesPage = ({resources}: {resources: Resource[]}) => (
    <div>
        <h3>Useful information and software</h3>
        {resources.map(r => <Resource key={r.name} resource={r} />)}
    </div>
)

const AboutPage = () => (
    <div>
        <h2>What's the point?</h2>

        <p>Many older books are available free online due to their copyright
        expiring. This site makes it easy to find them in epub, Kindle, and PDF
            format.

        If not available for free, it shows popular websites where you can
        buy them.</p>
    </div>
)

const Menu = () => (
    <div />
)

// todo state type should be MainState from index.tsx.
export const Main = ({store, state, dispatch}: {store: any, state: any, dispatch: Function}) => {
    console.log(state.books, "ALL")

    const findPage = (page) => {
        switch(page) {
            case 'home':
                return <HomePage books={state.books} />
            case 'resources':
                return <ResourcesPage resources={state.resources} />
            case 'about':
                return <AboutPage />
            default:
                return <HomePage books={state.books} />
        }
    }
    const activePage = findPage(state.activePage)

    // we sort out how not to hvae it local.
    return (
        <div>
            <Grid>
                <Row
                    className="show-grid"
                >
                    <Col sm={12}>
                        <Menu />
                    </Col>
                </Row>

                <Row
                    className="show-grid"
                >
                    <Col
                        sm={10}
                        smOffset={1}
                    >
                        {activePage}
                    </Col>
                </Row>
            </Grid>
        </div>

    )
}

export function get(url: string, callback: any=() => null) {
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

export default Main
