import * as React from 'react'

import DjangoCSRFToken from 'django-react-csrftoken'

import {Button, Grid, Row, Col, Clearfix,
    Form, FormGroup, FormControl, ControlLabel, ButtonGroup,
    DropdownButton, MenuItem} from 'react-bootstrap'

import * as _ from 'lodash'
import {Work, MainState, Resource} from "./interfaces"
import axios from "axios"

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

const Book = ({book}: {book: Work}) => (
    <div style={{marginTop: 40}}>
        <h4>{book.title}, written by: {book.author.last_name}</h4>

        <div style={{float: 'left', width: 300, height: 100, background: 'teal'}}>
            <h3>Information</h3>
            <a href={''}>Wikipedia</a>
            <a href={''}>Wikipedia</a>
        </div>

        <div style={{float: 'left', width: 300, height: 100, background: 'salmon'}}>
            <h3>Stores</h3>
            <a href={''}>Amazon</a>
            Kobo?
            Google

        </div>

    </div>
)

const HomePage = ({books}: {books: Work[]}) => (
    <div>
        <h1>Find ebooks</h1>

        <SearchForm />

        {books.map(b => <Book key={b.id} book={b}/>)}
    </div>
)

const Resource = ({resource}: {resource: Resource}) => (
    <div style={{marginBottom: 40}}>
        <h3>{resource.name}</h3>
        <p>{resource.description}</p>
        <p>
            <a href={resource.website_url}>Website</a>
        </p>
        <p>
            <a href={resource.download_url}>Download</a>
        </p>
    </div>
)

const ResourcesPage = ({resources}: {resources: Resource[]}) => (
    <div>
        <h3>Useful information and software</h3>
        {resources.map(r => <Resource key={r.name} resource={r} />)}
    </div>
)

 // todo: Make about page text a database entry.
const AboutPage = () => (
    <div>
        <h2>What's the point?</h2>

        <p>Many older books are available free online due to their copyright
            expiring. This site makes it easy to find them in epub, Kindle, and PDF
            format.

            An important part is to show only what you search for: Ie only the cleanest
            Version, with no extraneous results.

            If not available for free, it shows popular websites where you can
            buy them.</p>

        <p>
            Special thanks to:

            -Project Gutenberg, for its excellent library of
            free books, and for providing tools to search their database.

            -Google, for their Books search tools.
        </p>
    </div>
)

const Menu = ({dispatch}: {dispatch: Function}) => (
    <Col sm={6} smOffset={4}>
        <ButtonGroup>
            <Button
                onClick={() => {
                dispatch({type: 'changePage', page: 'home'})

                axios.get('http://localhost:8000/api/books').then(
                    (resp) =>
                        dispatch({
                            type: 'replaceBooks',
                            books: resp.data.results
                        })
                )
                }}
            >
                Home
            </Button>
            <Button onClick={() => dispatch({type: 'changePage', page: 'resources'})}>Resources</Button>
            <Button onClick={() => dispatch({type: 'changePage', page: 'about'})}>About</Button>
        </ButtonGroup>
    </Col>
)

export const Main = ({state, dispatch}: {state: MainState, dispatch: Function}) => {
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
    const activePage = findPage(state.page)

    return (
        <div>
            <Grid>
                <Row className="show-grid">

                    <Menu dispatch={dispatch} />

                </Row>

                <Row className="show-grid">
                    <Col sm={10} smOffset={1}>
                        {activePage}
                    </Col>
                </Row>
            </Grid>
        </div>

    )
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
    // axios.post('http://127.0.0.1:8000/main/search', data, success)
}

export default Main
