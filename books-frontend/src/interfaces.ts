// From Django models:
export interface Author {
    id: number
    first_name: string
    last_name: string
}

export interface Source {
    name: string
    url: string
    information: boolean
    free_downloads: boolean
    purchases: boolean
}

export interface WorkSource {
    id: number
    source: Source
    epub_avail: boolean
    kindle_avail: boolean
    book_url: string
    download_url: string
    price: number
}

export interface Work {
    id: number
    title: string
    author: Author
    genre: string
    description: string
    work_sources: WorkSource[]
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
    books: Work[]
    resources: Resource[]
}