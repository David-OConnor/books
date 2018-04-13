import * as React from 'react'

import {Button, Grid, Row, Col,
    Form, FormGroup, FormControl,ButtonGroup} from 'react-bootstrap'

// import * as _ from 'lodash'
import {Work, MainState, Resource} from "./interfaces"
import axios from "axios"

import * as Spinner from "react-spinkit"
// import { RingLoader } from 'react-spinners';

interface SearchProps {
    dispatch: Function
}

interface SearchState {
    value: string
    title: string
    author: string
}

class SearchForm extends React.Component<SearchProps, SearchState> {
    // todo make this one search field instead of separate title and author.
    constructor(props: SearchProps) {
        super(props);
        this.state = {
            value: '',
            title: '',
            author: '',
        }

        this.handleChangeTitle = this.handleChangeTitle.bind(this)
        this.handleChangeAuthor = this.handleChangeAuthor.bind(this)
    }

    handleChangeTitle(event: any) {
        this.setState({title: event.target.value})
    }

    handleChangeAuthor(event: any) {
        this.setState({author: event.target.value})
    }

    render() {
        const dispatch = this.props.dispatch
        return (
            <Form inline={true} style={{textAlign: 'center'}}>
                {/*<h4>Search by title, author, or ISBN:</h4>*/}
                <h4>Search by title and/or author:</h4>
                <FormGroup controlId="searchBox" >
                    {/*<ControlLabel>Search by title, author, or ISBN:</ControlLabel>*/}
                    <FormControl
                        type="text"
                        value={this.state.title}
                        placeholder="title"
                        onChange={this.handleChangeTitle}
                    />
                    <FormControl.Feedback />

                    <FormControl
                        type="text"
                        value={this.state.author}
                        placeholder="author"
                        onChange={this.handleChangeAuthor}
                    />
                    <FormControl.Feedback />

                    {/* type as submit so enter works, but preventdefault to prevent
                    the associated page reload. */}
                    <Button
                        type="submit"
                        bsStyle="primary"
                        onClick={(e: any) => {
                            e.preventDefault()
                            dispatch({
                                type: 'setDisplaying',
                                on: false
                            })
                            dispatch({
                                type: 'setLoading',
                                on: true
                            })

                            dispatch({
                                type: 'replaceBooks',
                                books: []
                            })

                            axios.post(
                                'http://localhost:8000/api/search',
                                {title: this.state.title, author: this.state.author}
                            ).then(
                                (resp) => {
                                    dispatch({
                                        type: 'setDisplaying',
                                        on: true
                                    })
                                    dispatch({
                                        type: 'setLoading',
                                        on: false
                                    })

                                    dispatch({
                                        type: 'replaceBooks',
                                        books: resp.data
                                    })}
                            )}}
                    >Search
                    </Button>
                </FormGroup>

            </Form>
        )
    }
}

const Book = ({book}: {book: Work}) => {
    // todo add description, genre, cover etc here.
    const indent = 20

    const infoSources = book.work_sources.filter(ws => ws.book_url)
    const infoItems = infoSources.map(ws =>
        (
            <div key={ws.id}>
                <h4><a href={ws.book_url}>{ws.source.name}</a></h4>
                {/*<p style={{textIndent: indent}}>*/}
                    {/*{ws.book_url ? <a href={ws.book_url}>Info</a> : null}*/}
                {/*</p>*/}
            </div>
        )
    )

    const freeSources = book.work_sources.filter(
        ws => ws.epub_url || ws.kindle_url || ws.pdf_url
    )
    const freeItems = freeSources.map(ws =>
        (
            <div key={ws.id}>
                <h4>{ws.source.name}</h4>
                <p style={{textIndent: indent}}>
                    {ws.epub_url ? <a href={ws.epub_url}>Epub</a> : null}
                </p>
                <p style={{textIndent: indent}}>
                    {ws.pdf_url ? <a href={ws.pdf_url}>Pdf</a> : null}
                </p>
                <p style={{textIndent: indent}}>
                    {ws.kindle_url ? <a href={ws.kindle_url}>Kindle</a> : null}
                </p>
            </div>
        )
    )

    const purchaseSources = book.work_sources.filter(ws => ws.purchase_url)
    // todo sort by price, ascending
    const purchaseItems = purchaseSources.map(ws =>
        (
            <div key={ws.id}>
                <h4>{ws.source.name}</h4>
                <p style={{textIndent: indent}}>
                    {ws.purchase_url ? <a href={ws.purchase_url}>Buy for ${ws.price}</a> : null}
                </p>
            </div>
        )
    )

    return (
        <div>
            <Row style={{marginTop: 40}}>
                <Col xs={12}>
                    <h4>{book.title}, by: {`${book.author.first_name} ${book.author.last_name}`}</h4>
                </Col>
            </Row>

            <Row
                style={{
                    display: 'flex',
                    // flexWrap: 'wrap',
                    borderStyle: 'solid',
                    borderWidth: 2,
                }}
            >

                <Col xs={4} style={{background: '#ffefcc'}}>
                    <h4>Information</h4>
                    {infoItems}
                </Col>

                <Col
                    xs={4}
                    style={{
                        background: '#eeeeff',
                        // display: 'flex',
                        // flexDirection: 'column',
                        borderLeftStyle: 'solid',
                        borderLeftWidth: 1,
                        borderLeftColor: '#888888',
                        borderRightStyle: 'solid',
                        borderRightWidth: 1,
                        borderRightColor: '#888888'
                    }}
                >

                    <h4>Free downloads</h4>
                    {freeItems.length ? freeItems : <h5>No free sources available 🙁 </h5>}
                </Col>

                <Col xs={4} style={{background: '#e3ffeb'}}>
                    <h4>Stores</h4>
                    {purchaseItems}
                </Col>

            </Row>
        </div>
    )
}

const HomePage = ({books, dispatch, loading, displayingResults}:
                      {books: Work[], dispatch: Function, loading: boolean, displayingResults: boolean}) => (
    <Col sm={12} style={{textAlign: 'center'}}>
        <h1 style={{margin: 'auto', marginBottom: 10}}>Find and download ebooks</h1>
        <h3 style={{margin: 'auto', marginBottom: 10, color: '#d89d55'}}>Beta</h3>

        <Row style={{textAlign: 'center', marginBottom: 40}}>
            <Col md={8} mdOffset={2} style={{marginBottom: 30}}>
                <SearchForm dispatch={dispatch} />
            </Col>

            <Col xs={12} md={8} mdOffset={2}>
                {/* todo ts is complaining about Spinner having style :/ */}
                {/*{loading ? (<Spinner name='circle' color='blue' style={{margin: 'auto'}}/> as any) : null}*/}
                <div style={{margin: 'auto'}}>
                    {loading ? <Spinner name='circle' color='blue'/> : null}
                </div>
                {/* Can't get ringloader to center. */}
                {/*<RingLoader*/}
                {/*color={'#123abc'}*/}
                {/*loading={true}*/}
                {/*/>*/}
                {!books.length && displayingResults ? <h4>No books found 🙁</h4> : null}

                {books.map(b => <Book key={b.id} book={b}/>)}

                {books.length && displayingResults ?
                    <h4>Don't see what you're looking for? 😕
                        <a
                            style={{cursor: 'pointer'}}
                            onClick={() => {
                                // todo Probably should pass title/author searched for
                                axios.post('http://localhost:8000/api/report', {books: books}).then(
                                    (resp) => {
                                        // todo instead, show the user a success message.
                                        console.log("Successfully submitted")
                                    }
                                )
                            }}
                        > Report
                        </a>
                    </h4>
                    : null}
            </Col>
        </Row>
    </Col>
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
    <Col xs={12} md={8} mdOffset={2}>
        <h3>Useful information and software</h3>
        {resources.map(r => <Resource key={r.name} resource={r} />)}
    </Col>
)

// todo: Make about page text a database entry.
const AboutPage = () => (
    <Col xs={12} md={8} mdOffset={2}>
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
    </Col>
)

const Menu = ({dispatch}: {dispatch: Function}) => (
    <Col xs={8} xsOffset={2} style={{textAlign: 'center', marginBottom: 30}}>
        <ButtonGroup>
            <Button
                onClick={() => dispatch({type: 'changePage', page: 'home'})}
            >
                Home
            </Button>
            <Button onClick={() => dispatch({type: 'changePage', page: 'resources'})}>Resources</Button>
            <Button onClick={() => dispatch({type: 'changePage', page: 'about'})}>About</Button>
        </ButtonGroup>
    </Col>
)

export const Main = ({state, dispatch}: {state: MainState, dispatch: Function}) => {
    const home = (
        <HomePage
            books={state.books}
            dispatch={dispatch}
            loading={state.loading}
            displayingResults={state.displayingResults}
        />
    )

    const findPage = (page: string) => {
        switch(page) {
            case 'home':
                return home
            case 'resources':
                return <ResourcesPage resources={state.resources} />
            case 'about':
                return <AboutPage />
            default:
                return home
        }
    }
    const activePage = findPage(state.page)

    return (
        <div>
            <Grid>
                <Row>
                    <Menu dispatch={dispatch} />
                </Row>

                <Row>
                    {activePage}
                </Row>
            </Grid>
        </div>
    )
}

export default Main
