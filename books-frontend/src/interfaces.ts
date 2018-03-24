// From Django models:
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

// Other interfaces:
export interface MainState {
    page: string
    books: Book2[]
    resources: Resource[]
}