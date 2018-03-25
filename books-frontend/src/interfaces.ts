// From Django models:
export interface Author {
    id: number
    first_name: string
    last_name: string
}

export interface Work {
    id: number
    title: string
    author: Author
    description: string

    // copyright_exp_us: string // date in format YYYY-MM-DD
    // copyright_expired: boolean
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