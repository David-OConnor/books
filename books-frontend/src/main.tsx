import * as React from 'react'

import {Button, Grid, Row, Col, Clearfix,
    Form, FormGroup, FormControl, ControlLabel, ButtonGroup,
    DropdownButton, MenuItem} from 'react-bootstrap'

import * as _ from 'lodash'
import {Work, MainState, Resource, WorkSource} from "./interfaces"
import axios from "axios"

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

    handleChangeTitle(event) {
        this.setState({title: event.target.value})
    }

    handleChangeAuthor(event) {
        this.setState({author: event.target.value})
    }

    render() {
        return (
            <Form inline={true} style={{textAlign: 'center'}}>
                <h4>Search by title, author, or ISBN:</h4>
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
                        onClick={(e) => {
                            e.preventDefault()

                            axios.post(
                                'http://localhost:8000/api/search',
                                {title: this.state.title, author: this.state.author}
                            ).then(
                                (resp) => {
                                    this.props.dispatch({
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
                <h4><a href={ws.source.url}>{ws.source.name}</a></h4>
                <p style={{textIndent: indent}}>
                    {ws.book_url ? <a href={ws.book_url}>Info</a> : null}
                </p>
            </div>
        )
    )

    const freeSources = book.work_sources.filter(
        ws => ws.epub_url || ws.kindle_url || ws.pdf_url
    )
    const freeItems = freeSources.map(ws =>
        (
            <div key={ws.id}>
                <h4><a href={ws.source.url}>{ws.source.name}</a></h4>
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
    const purchaseItems = purchaseSources.map(ws =>
        (
            <div key={ws.id}>
                <h4><a href={ws.source.url}>{ws.source.name}</a></h4>
                <p style={{textIndent: indent}}>
                    {ws.purchase_url ? <a href={ws.purchase_url}>Buy for ${ws.price}</a> : null}
                </p>
            </div>
        )
    )

    //     <h5>No free sources available 🙁 </h5>

    return (
        <Row style={{marginTop: 40}}>
            <h4>{book.title},
                by: {`${book.author.first_name} ${book.author.last_name}`}</h4>

            <Col xs={4} style={{background: '#ffefcc'}}>
                <h4>Information</h4>
                {infoItems}
            </Col>

            <Col xs={4} style={{background: '#e8e7ff'}}>
                <h4>Free downloads</h4>
                {freeItems}
            </Col>

            <Col xs={4} style={{background: '#e3ffeb'}}>
                <h4>Stores</h4>
                {purchaseItems}
            </Col>

        </Row>
    )
}

const HomePage = ({books, dispatch}: {books: Work[], dispatch: Function}) => (
    <Col sm={12} smOffset={0} style={{textAlign: 'center'}}>
        <h1 style={{margin: 'auto'}}>Find and download ebooks</h1>

        <Row style={{textAlign: 'center'}}>
            <Col md={8} mdOffset={2}>
                <SearchForm dispatch={dispatch} />
            </Col>

            <Col xs={12} md={8} mdOffset={2}>
                {books.map(b => <Book key={b.id} book={b}/>)}
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
    <Col xs={8} xsOffset={2} style={{textAlign: 'center'}}>
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
    const findPage = (page) => {
        switch(page) {
            case 'home':
                return <HomePage books={state.books} dispatch={dispatch} />
            case 'resources':
                return <ResourcesPage resources={state.resources} />
            case 'about':
                return <AboutPage />
            default:
                return <HomePage books={state.books} dispatch={dispatch}/>
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
